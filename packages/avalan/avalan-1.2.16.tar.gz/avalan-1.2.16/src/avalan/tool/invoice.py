from avalan.tool import Tool
from babel.numbers import parse_decimal
from bs4 import BeautifulSoup
from dataclasses import dataclass
from dateutil.parser import parse, ParserError
from decimal import Decimal
from itertools import chain
from langextract import extract
from langextract.data import AlignmentStatus, ExampleData
from langextract.inference import OpenAILanguageModel
from logging import Logger
from marker.config.parser import ConfigParser
from marker.converters import BaseConverter
from marker.converters.table import TableConverter
from marker.models import create_model_dict
from typing import Any, Iterable


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceItem:
    code: str | None = None
    ean: str | None = None
    description: str | None = None
    quantity: int | None = None
    lot: str | None = None
    tax: float | None = None
    unit_currency: str | None = None
    unit_price: Decimal | None = None
    total_currency: str | None = None
    total_price: Decimal | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Invoice:
    date: str | None = None
    identifier: str | None = None
    identifiers: list[str] | None = None
    items: list[InvoiceItem] | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSettingSpec:
    prompt: str
    examples: list[ExampleData]


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSettingSpecs:
    header: InvoiceSettingSpec
    items: InvoiceSettingSpec


@dataclass(frozen=True, kw_only=True, slots=True)
class InvoiceSettings:
    specs: InvoiceSettingSpecs
    date_dayfirst: bool = False
    locale: str


class InvoiceParserTool(Tool):
    _converter: BaseConverter
    _extractor_params: dict
    _extractor_model_id: str
    _line_min_len: int
    _logger: Logger

    def __init__(
        self,
        *,
        api_url: str,
        api_key: str,
        extractor_api_url: str | None = None,
        extractor_api_key: str | None = None,
        extractor_model_id: str | None = "gpt-4o-mini",
        line_min_len: int = 6,
        logger: Logger,
        model_id: str,
        parser_concurrency: int = 1,
        parser_disable_progress: bool = False,
        parser_page_range: str | None = None,
        parser_retries: int = 3,
        parser_timeout: int | None = 300,
    ) -> None:
        super().__init__()
        self.__name__ = "invoice_parser"
        parser_config = {
            "max_concurrency": parser_concurrency,
            "disable_tqdm": parser_disable_progress,
            "output_format": "html",
            "disable_image_extraction": False,
            "page_range": parser_page_range,
            "use_llm": True,
            "llm_service": "marker.services.openai.OpenAIService",
            "timeout": parser_timeout,
            "max_retries": parser_retries,
            "openai_base_url": api_url,
            "openai_api_key": api_key,
            "openai_model": model_id,
        }
        self._extractor_params = {
            "api_key": extractor_api_key or api_key,
            "base_url": extractor_api_url or None,
        }
        self._extractor_model_id = extractor_model_id
        self._line_min_len = line_min_len
        self._logger = logger
        config_parser = ConfigParser(parser_config)
        self._converter = TableConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service(),
        )

    async def __call__(
        self,
        *,
        html: str | None = None,
        path: str | None = None,
        settings: InvoiceSettings,
    ) -> Invoice | None:
        assert html or path

        self._logger.info("Processing potential invoice %s", path)

        if not html:
            self._logger.debug("Converting %s with %s", path, self._converter)

            rendered = self._converter(path)
            html = rendered.html

            self._logger.debug("Converted %s with %s", path, self._converter)

        self._logger.debug("Parsing generated HTML from %s", path)

        soup = BeautifulSoup(html, "html.parser")
        tables = []

        for table in soup.find_all("table"):
            headers = None
            thead = table.find("thead")
            if thead:
                headers = [
                    cell.get_text(strip=True)
                    for cell in thead.find_all(["th", "td"])
                ]

            if not headers:
                first_row = table.find("tr")
                headers = [
                    cell.get_text(strip=True)
                    for cell in first_row.find_all("th")
                ]

            total_headers = len(headers)
            rows = []
            for tr in table.find_all("tr"):
                if headers and tr.find_parent("thead"):
                    continue
                cells = [
                    cell.get_text(strip=True)
                    for cell in tr.find_all(["td", "th"])
                ]
                if not cells:
                    continue

                if headers:
                    row = {
                        headers[i] if i < total_headers else f"col_{i}": cells[
                            i
                        ]
                        for i in range(len(cells))
                    }
                else:
                    row = cells

                rows.append(row)

            tables.append(rows)

        self._logger.debug("Parsed converted HTML from %s", path)

        if not tables:
            self._logger.info(
                "No tables found after parsing converted HTML from %s", path
            )
            return None

        extraction_settings = dict(
            language_model_type=OpenAILanguageModel,
            language_model_params=self._extractor_params,
            model_id=self._extractor_model_id,
            use_schema_constraints=False,
            fence_output=True,
            debug=False,
        )

        # Process header

        flattened_header = InvoiceParserTool._flatten(tables, lines=False)
        annotated_header = extract(
            prompt_description=settings.specs.header.prompt,
            examples=settings.specs.header.examples,
            text_or_documents=flattened_header,
            **extraction_settings,
        )

        identifiers = []
        identifier = None
        dates = []
        if annotated_header and annotated_header.extractions:
            for extraction in annotated_header.extractions:
                attributes = extraction.attributes
                if (
                    extraction.alignment_status == AlignmentStatus.MATCH_EXACT
                    and attributes
                    and "type" in attributes
                ):
                    if (
                        extraction.extraction_class == "code"
                        and "is_invoice" in attributes
                        and attributes["is_invoice"]
                    ):
                        if not identifier and (
                            "is_internal" not in attributes
                            or not attributes["is_internal"]
                        ):
                            identifier = extraction.extraction_text
                        identifiers.append(extraction.extraction_text)
                    elif extraction.extraction_class == "date":
                        try:
                            date = parse(
                                extraction.extraction_text,
                                dayfirst=settings.date_dayfirst,
                            ).strftime("%Y-%m-%d")
                            dates.append(extraction.extraction_text)
                        except ParserError:
                            pass

        if identifiers and identifier:
            identifiers.remove(identifier)

        date = min(set(dates)) if dates else None

        # Process lines

        items = []

        flattened_lines = InvoiceParserTool._flatten(tables, lines=True)
        annotated_lines = extract(
            prompt_description=settings.specs.items.prompt,
            examples=settings.specs.items.examples,
            text_or_documents=flattened_lines,
            **extraction_settings,
        )
        if annotated_lines and annotated_lines.extractions:
            for extraction in annotated_lines.extractions:
                attributes = extraction.attributes
                if (
                    extraction.alignment_status == AlignmentStatus.MATCH_EXACT
                    and extraction.extraction_class == "item"
                    and attributes
                    and "code" in attributes
                    and "quantity" in attributes
                    and "value" in attributes
                ):
                    currency = (
                        attributes["value_currency"]
                        if "value_currency" in attributes
                        and attributes["value_currency"]
                        else None
                    )
                    price = parse_decimal(attributes["value"], settings.locale)
                    total_currency = (
                        attributes["value_total_currency"]
                        if "value_total_currency" in attributes
                        and attributes["value_total_currency"]
                        else currency
                    )
                    total_price = (
                        parse_decimal(
                            attributes["value_total"], settings.locale
                        )
                        if "value_total" in attributes
                        and attributes["value_total"]
                        else price
                    )

                    item = InvoiceItem(
                        code=attributes["code"],
                        ean=(
                            attributes["ean"]
                            if "ean" in attributes and attributes["ean"]
                            else None
                        ),
                        description=(
                            attributes["description"]
                            if "description" in attributes
                            and attributes["description"]
                            else None
                        ),
                        quantity=attributes["quantity"],
                        lot=(
                            attributes["lot"]
                            if "lot" in attributes and attributes["lot"]
                            else None
                        ),
                        tax=(
                            attributes["tax"]
                            if "tax" in attributes and attributes["tax"]
                            else None
                        ),
                        unit_currency=currency,
                        unit_price=price,
                        total_currency=total_currency,
                        total_price=total_price,
                    )
                    items.append(item)

        # Build invoice

        invoice = Invoice(
            date=date,
            identifier=identifier,
            identifiers=identifiers,
            items=items,
        )

        self._logger.info("Processed invoice from %s as %s", path, invoice)

        return invoice

    @staticmethod
    def _flatten(data: Iterable[Any], lines: bool) -> str:
        make_lines = (
            (
                InvoiceParserTool._from_string_row(r)
                if isinstance(r, list)
                else InvoiceParserTool._from_dict_row(r, lines)
            )
            for r in InvoiceParserTool._iter_items(data)
            if not (lines and isinstance(r, list))
        )
        lines = chain.from_iterable(make_lines)
        return "\n".join(f"* {line}" for line in lines if line)

    @staticmethod
    def _iter_items(tree: Iterable[Any]) -> Iterable[Any]:
        for obj in tree:
            if isinstance(obj, list):
                if obj and all(isinstance(x, str) for x in obj):
                    yield obj
                else:
                    yield from InvoiceParserTool._iter_items(obj)
            else:
                yield obj

    @staticmethod
    def _from_string_row(row: list[str]) -> list[str]:
        out, i = [], 0
        while i < len(row):
            text = row[i].strip()
            if text.endswith(":"):
                nxt = row[i + 1].strip() if i + 1 < len(row) else ""
                out.append(f"{text} {nxt}".strip())
                i += 2
            else:
                out.append(text)
                i += 1
        return out

    @staticmethod
    def _from_dict_row(d: dict[str, str], lines: bool) -> list[str]:
        length = len(d)
        if (not lines and length >= self._line_min_len) or (
            lines and length < self._line_min_len
        ):
            return []

        current_lines = []
        for k, v in d.items():
            k, v = k.strip(), v.strip()
            if not v:
                current_lines.append(f"{k}: {v}")
            elif k.rstrip(":") == v:
                current_lines.append(k)
            else:
                sep = "" if k.endswith(":") else ":"
                current_lines.append(f"{k}{sep} {v}")

        if lines:
            current_lines = [" | ".join(current_lines)]

        return current_lines
