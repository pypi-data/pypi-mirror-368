from ..entities import (
    AttentionImplementation,
    EngineUri,
    GenerationSettings,
    ChatSettings,
    ReasoningSettings,
    ReasoningTag,
    Input,
    Modality,
    Operation,
    OperationAudioParameters,
    OperationParameters,
    OperationTextParameters,
    OperationVisionParameters,
    ParallelStrategy,
    Backend,
    TextGenerationLoaderClass,
    TransformerEngineSettings,
    Vendor,
    WeightType,
)
from ..model.hubs.huggingface import HuggingfaceHub
from ..model.nlp.sentence import SentenceTransformerModel
from ..model.nlp.text.generation import TextGenerationModel
from ..model.nlp.text.mlxlm import MlxLmModel
from ..model.nlp.question import QuestionAnsweringModel
from ..model.nlp.sequence import (
    SequenceClassificationModel,
    SequenceToSequenceModel,
    TranslationModel,
)
from ..model.nlp.token import TokenClassificationModel
from ..model.audio.classification import AudioClassificationModel
from ..model.audio.generation import AudioGenerationModel
from ..model.audio.speech_recognition import SpeechRecognitionModel
from ..model.audio.speech import TextToSpeechModel
from ..model.criteria import KeywordStoppingCriteria
from ..model.vision.detection import ObjectDetectionModel
from ..model.vision.classification import ImageClassificationModel
from ..model.vision.decoder import VisionEncoderDecoderModel
from ..model.vision.diffusion import (
    TextToAnimationModel,
    TextToImageModel,
    TextToVideoModel,
)
from ..model.vision.segmentation import SemanticSegmentationModel
from ..model.vision.text import ImageTextToTextModel, ImageToTextModel
from ..secrets import KeyringSecrets
from ..tool.manager import ToolManager
from ..event import Event, EventType
from ..event.manager import EventManager
from argparse import Namespace
from contextlib import ContextDecorator, ExitStack
from logging import Logger
from typing import Any, get_args, TypeAlias
from time import perf_counter
from urllib.parse import parse_qsl, urlparse

ModelType: TypeAlias = (
    AudioClassificationModel
    | AudioGenerationModel
    | ImageClassificationModel
    | ImageTextToTextModel
    | ImageToTextModel
    | ObjectDetectionModel
    | QuestionAnsweringModel
    | SemanticSegmentationModel
    | SentenceTransformerModel
    | SequenceClassificationModel
    | SequenceToSequenceModel
    | SpeechRecognitionModel
    | AudioGenerationModel
    | TextGenerationModel
    | TextToImageModel
    | TextToSpeechModel
    | TranslationModel
    | TokenClassificationModel
    | VisionEncoderDecoderModel
    | TextToAnimationModel
    | TextToVideoModel
)


class ModelManager(ContextDecorator):
    _hub: HuggingfaceHub
    _stack: ExitStack
    _logger: Logger
    _secrets: KeyringSecrets
    _event_manager: EventManager | None

    def __init__(
        self,
        hub: HuggingfaceHub,
        logger: Logger,
        secrets: KeyringSecrets | None = None,
        event_manager: EventManager | None = None,
    ):
        self._hub, self._logger = hub, logger
        self._stack = ExitStack()
        self._secrets = secrets or KeyringSecrets()
        self._event_manager = event_manager

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any | None,
    ):
        return self._stack.__exit__(exc_type, exc_value, traceback)

    async def __call__(
        self,
        engine_uri: EngineUri,
        model: ModelType,
        operation: Operation,
        tool: ToolManager | None = None,
    ):
        modality = operation.modality

        self._logger.info("ModelManager call process started for %s", modality)

        stopping_criteria = (
            KeywordStoppingCriteria(
                operation.parameters["text"].stop_on_keywords,
                model.tokenizer,
            )
            if operation.parameters
            and "text" in operation.parameters
            and operation.parameters["text"]
            and operation.parameters["text"].stop_on_keywords
            else None
        )

        start = perf_counter()
        if self._event_manager:
            await self._event_manager.trigger(
                Event(
                    type=EventType.MODEL_MANAGER_CALL_BEFORE,
                    payload={
                        "engine_uri": engine_uri,
                        "modality": modality,
                        "operation": operation,
                    },
                    started=start,
                )
            )

        result: Any

        match modality:
            case Modality.AUDIO_CLASSIFICATION:
                assert (
                    operation.parameters["audio"]
                    and operation.parameters["audio"].path
                    and operation.parameters["audio"].sampling_rate
                )

                result = await model(
                    path=operation.parameters["audio"].path,
                    sampling_rate=operation.parameters["audio"].sampling_rate,
                )

            case Modality.AUDIO_SPEECH_RECOGNITION:
                assert (
                    operation.parameters["audio"]
                    and operation.parameters["audio"].path
                    and operation.parameters["audio"].sampling_rate
                )

                result = await model(
                    path=operation.parameters["audio"].path,
                    sampling_rate=operation.parameters["audio"].sampling_rate,
                )

            case Modality.AUDIO_TEXT_TO_SPEECH:
                assert (
                    operation.parameters["audio"]
                    and operation.parameters["audio"].path
                    and operation.parameters["audio"].sampling_rate
                )

                result = await model(
                    path=operation.parameters["audio"].path,
                    prompt=operation.input,
                    max_new_tokens=operation.generation_settings.max_new_tokens,
                    reference_path=operation.parameters[
                        "audio"
                    ].reference_path,
                    reference_text=operation.parameters[
                        "audio"
                    ].reference_text,
                    sampling_rate=operation.parameters["audio"].sampling_rate,
                )

            case Modality.AUDIO_GENERATION:
                assert (
                    operation.input
                    and operation.parameters["audio"]
                    and operation.parameters["audio"].path
                )

                result = await model(
                    operation.input,
                    operation.parameters["audio"].path,
                    operation.generation_settings.max_new_tokens,
                )

            case Modality.TEXT_GENERATION:
                assert operation.input and operation.parameters["text"]

                is_mlx = isinstance(model, MlxLmModel)
                if engine_uri.is_local and not is_mlx:
                    result = await model(
                        operation.input,
                        system_prompt=operation.parameters[
                            "text"
                        ].system_prompt,
                        settings=operation.generation_settings,
                        stopping_criterias=(
                            [stopping_criteria] if stopping_criteria else None
                        ),
                        manual_sampling=operation.parameters[
                            "text"
                        ].manual_sampling,
                        pick=operation.parameters["text"].pick_tokens,
                        skip_special_tokens=operation.parameters[
                            "text"
                        ].skip_special_tokens,
                        tool=tool,
                    )
                else:
                    result = await model(
                        operation.input,
                        system_prompt=operation.parameters[
                            "text"
                        ].system_prompt,
                        settings=operation.generation_settings,
                        tool=tool,
                    )

            case Modality.TEXT_QUESTION_ANSWERING:
                assert (
                    operation.input
                    and operation.parameters["text"]
                    and operation.parameters["text"].context
                )

                result = await model(
                    operation.input,
                    context=operation.parameters["text"].context,
                    system_prompt=operation.parameters["text"].system_prompt,
                )

            case Modality.TEXT_SEQUENCE_CLASSIFICATION:
                assert operation.input

                result = await model(operation.input)

            case Modality.TEXT_SEQUENCE_TO_SEQUENCE:
                assert operation.input and operation.parameters["text"]

                result = await model(
                    operation.input,
                    settings=operation.generation_settings,
                    stopping_criterias=(
                        [stopping_criteria] if stopping_criteria else None
                    ),
                )

            case Modality.TEXT_TOKEN_CLASSIFICATION:
                assert operation.input and operation.parameters["text"]

                result = await model(
                    operation.input,
                    labeled_only=operation.parameters["text"].labeled_only
                    or False,
                    system_prompt=operation.parameters["text"].system_prompt,
                )

            case Modality.TEXT_TRANSLATION:
                assert (
                    operation.input
                    and operation.parameters["text"]
                    and operation.parameters["text"].language_source
                    and operation.parameters["text"].language_destination
                )

                result = await model(
                    operation.input,
                    source_language=operation.parameters[
                        "text"
                    ].language_source,
                    destination_language=operation.parameters[
                        "text"
                    ].language_destination,
                    settings=operation.generation_settings,
                    stopping_criterias=(
                        [stopping_criteria] if stopping_criteria else None
                    ),
                    skip_special_tokens=operation.parameters[
                        "text"
                    ].skip_special_tokens,
                )

            case Modality.VISION_ENCODER_DECODER:
                assert (
                    operation.parameters["vision"]
                    and operation.parameters["vision"].path
                )

                result = await model(
                    operation.parameters["vision"].path,
                    prompt=operation.input,
                    skip_special_tokens=operation.parameters[
                        "vision"
                    ].skip_special_tokens,
                )

            case Modality.VISION_IMAGE_CLASSIFICATION:
                assert (
                    operation.parameters["vision"]
                    and operation.parameters["vision"].path
                )

                result = await model(operation.parameters["vision"].path)

            case Modality.VISION_IMAGE_TO_TEXT:
                assert (
                    operation.parameters["vision"]
                    and operation.parameters["vision"].path
                )

                result = await model(
                    operation.parameters["vision"].path,
                    skip_special_tokens=operation.parameters[
                        "vision"
                    ].skip_special_tokens,
                )

            case Modality.VISION_IMAGE_TEXT_TO_TEXT:
                assert (
                    operation.parameters["vision"]
                    and operation.parameters["vision"].path
                )

                result = await model(
                    operation.parameters["vision"].path,
                    operation.input,
                    system_prompt=operation.parameters["vision"].system_prompt,
                    settings=operation.generation_settings,
                    width=operation.parameters["vision"].width,
                )

            case Modality.VISION_OBJECT_DETECTION:
                assert (
                    operation.parameters["vision"]
                    and operation.parameters["vision"].path
                    and operation.parameters["vision"].threshold is not None
                )

                result = await model(
                    operation.parameters["vision"].path,
                    threshold=operation.parameters["vision"].threshold,
                )

            case Modality.VISION_TEXT_TO_IMAGE:
                assert (
                    operation.input
                    and operation.parameters["vision"]
                    and operation.parameters["vision"].path
                    and operation.parameters["vision"].color_model
                    and operation.parameters["vision"].high_noise_frac
                    is not None
                    and operation.parameters["vision"].image_format
                    and operation.parameters["vision"].n_steps is not None
                )

                result = await model(
                    operation.input,
                    operation.parameters["vision"].path,
                    color_model=operation.parameters["vision"].color_model,
                    high_noise_frac=operation.parameters[
                        "vision"
                    ].high_noise_frac,
                    image_format=operation.parameters["vision"].image_format,
                    n_steps=operation.parameters["vision"].n_steps,
                )

            case Modality.VISION_TEXT_TO_ANIMATION:
                assert (
                    operation.input
                    and operation.parameters["vision"]
                    and operation.parameters["vision"].path
                    and operation.parameters["vision"].n_steps is not None
                    and operation.parameters["vision"].timestep_spacing
                    and operation.parameters["vision"].beta_schedule
                    and operation.parameters["vision"].guidance_scale
                    is not None
                )

                result = await model(
                    operation.input,
                    operation.parameters["vision"].path,
                    beta_schedule=operation.parameters["vision"].beta_schedule,
                    guidance_scale=operation.parameters[
                        "vision"
                    ].guidance_scale,
                    steps=operation.parameters["vision"].n_steps,
                    timestep_spacing=operation.parameters[
                        "vision"
                    ].timestep_spacing,
                )

            case Modality.VISION_TEXT_TO_VIDEO:
                assert (
                    operation.input
                    and operation.parameters["vision"]
                    and operation.parameters["vision"].path
                )

                vision = operation.parameters["vision"]
                kwargs = {
                    "reference_path": vision.reference_path,
                    "negative_prompt": vision.negative_prompt,
                    "height": vision.height,
                    "downscale": vision.downscale,
                    "frames": vision.frames,
                    "denoise_strength": vision.denoise_strength,
                    "inference_steps": vision.inference_steps,
                    "decode_timestep": vision.decode_timestep,
                    "noise_scale": vision.noise_scale,
                    "frames_per_second": vision.frames_per_second,
                }
                if vision.width is not None:
                    kwargs["width"] = vision.width
                if vision.n_steps is not None:
                    kwargs["steps"] = vision.n_steps

                result = await model(
                    operation.input,
                    vision.path,
                    **kwargs,
                )

            case Modality.VISION_SEMANTIC_SEGMENTATION:
                assert (
                    operation.parameters["vision"]
                    and operation.parameters["vision"].path
                )

                result = await model(operation.parameters["vision"].path)

            case _:
                raise NotImplementedError(f"Modality {modality} not supported")

        end = perf_counter()
        if self._event_manager:
            await self._event_manager.trigger(
                Event(
                    type=EventType.MODEL_MANAGER_CALL_AFTER,
                    payload={
                        "engine_uri": engine_uri,
                        "modality": modality,
                        "operation": operation,
                        "result": result,
                    },
                    started=start,
                    finished=end,
                    elapsed=end - start,
                )
            )

        self._logger.info("ModelManager call processed for %s", modality)

        return result

    @staticmethod
    def get_operation_from_arguments(
        modality: Modality,
        args: Namespace,
        input_string: Input | None,
    ) -> Operation:
        reasoning_settings = ReasoningSettings(
            max_new_tokens=getattr(args, "reasoning_max_new_tokens", None),
            enabled=not getattr(args, "no_reasoning", False),
            stop_on_max_new_tokens=getattr(
                args,
                "reasoning_stop_on_max_new_tokens",
                False,
            ),
            tag=(
                ReasoningTag(getattr(args, "reasoning_tag"))
                if getattr(args, "reasoning_tag", None)
                else None
            ),
        )
        settings = GenerationSettings(
            do_sample=args.do_sample,
            enable_gradient_calculation=args.enable_gradient_calculation,
            max_new_tokens=args.max_new_tokens,
            max_length=getattr(args, "text_max_length", None),
            min_p=args.min_p,
            num_beams=getattr(args, "text_num_beams", None),
            repetition_penalty=args.repetition_penalty,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            use_cache=args.use_cache,
            chat_settings=ChatSettings(
                enable_thinking=not getattr(
                    args,
                    "chat_disable_thinking",
                    not reasoning_settings.enabled,
                )
            ),
            reasoning=reasoning_settings,
        )
        system_prompt = args.system or None

        requires_input = modality in {
            Modality.AUDIO_TEXT_TO_SPEECH,
            Modality.AUDIO_GENERATION,
            Modality.TEXT_GENERATION,
            Modality.TEXT_QUESTION_ANSWERING,
            Modality.TEXT_SEQUENCE_CLASSIFICATION,
            Modality.TEXT_SEQUENCE_TO_SEQUENCE,
            Modality.TEXT_TRANSLATION,
            Modality.TEXT_TOKEN_CLASSIFICATION,
            Modality.VISION_IMAGE_TEXT_TO_TEXT,
            Modality.VISION_TEXT_TO_IMAGE,
            Modality.VISION_TEXT_TO_ANIMATION,
            Modality.VISION_TEXT_TO_VIDEO,
        }

        match modality:
            case Modality.AUDIO_CLASSIFICATION:
                parameters = OperationParameters(
                    audio=OperationAudioParameters(
                        path=args.path,
                        sampling_rate=args.audio_sampling_rate,
                    )
                )

            case Modality.AUDIO_SPEECH_RECOGNITION:
                parameters = OperationParameters(
                    audio=OperationAudioParameters(
                        path=args.path,
                        sampling_rate=args.audio_sampling_rate,
                    )
                )

            case Modality.AUDIO_TEXT_TO_SPEECH:
                parameters = OperationParameters(
                    audio=OperationAudioParameters(
                        path=args.path,
                        reference_path=args.audio_reference_path,
                        reference_text=args.audio_reference_text,
                        sampling_rate=args.audio_sampling_rate,
                    )
                )

            case Modality.AUDIO_GENERATION:
                parameters = OperationParameters(
                    audio=OperationAudioParameters(
                        path=args.path,
                        sampling_rate=args.audio_sampling_rate,
                    )
                )

            case Modality.TEXT_QUESTION_ANSWERING:
                parameters = OperationParameters(
                    text=OperationTextParameters(
                        context=args.text_context,
                        system_prompt=system_prompt,
                    )
                )

            case Modality.TEXT_SEQUENCE_CLASSIFICATION:
                parameters = None

            case Modality.TEXT_SEQUENCE_TO_SEQUENCE:
                parameters = OperationParameters(
                    text=OperationTextParameters(
                        stop_on_keywords=args.stop_on_keyword,
                    )
                )

            case Modality.TEXT_TRANSLATION:
                parameters = OperationParameters(
                    text=OperationTextParameters(
                        language_destination=args.text_to_lang,
                        language_source=args.text_from_lang,
                        stop_on_keywords=args.stop_on_keyword,
                        skip_special_tokens=args.skip_special_tokens,
                    )
                )

            case Modality.TEXT_TOKEN_CLASSIFICATION:
                parameters = OperationParameters(
                    text=OperationTextParameters(
                        labeled_only=getattr(args, "text_labeled_only", None),
                        system_prompt=system_prompt,
                    )
                )

            case Modality.TEXT_GENERATION:
                parameters = OperationParameters(
                    text=OperationTextParameters(
                        manual_sampling=args.display_tokens or 0,
                        pick_tokens=(
                            10
                            if args.display_tokens and args.display_tokens > 0
                            else 0
                        ),
                        stop_on_keywords=args.stop_on_keyword,
                        skip_special_tokens=args.quiet
                        or args.skip_special_tokens,
                        system_prompt=system_prompt,
                    )
                )

            case Modality.VISION_IMAGE_CLASSIFICATION:
                parameters = OperationParameters(
                    vision=OperationVisionParameters(
                        path=args.path,
                    )
                )

            case (
                Modality.VISION_IMAGE_TO_TEXT | Modality.VISION_ENCODER_DECODER
            ):
                parameters = OperationParameters(
                    vision=OperationVisionParameters(
                        path=args.path,
                        skip_special_tokens=args.skip_special_tokens,
                    )
                )

            case Modality.VISION_IMAGE_TEXT_TO_TEXT:
                parameters = OperationParameters(
                    vision=OperationVisionParameters(
                        path=args.path,
                        system_prompt=system_prompt,
                        width=getattr(
                            args,
                            "vision_width",
                            getattr(args, "image_width", None),
                        ),
                    )
                )

            case Modality.VISION_OBJECT_DETECTION:
                parameters = OperationParameters(
                    vision=OperationVisionParameters(
                        path=args.path,
                        threshold=getattr(
                            args,
                            "vision_threshold",
                            getattr(args, "image_threshold", None),
                        ),
                    )
                )

            case Modality.VISION_TEXT_TO_IMAGE:
                parameters = OperationParameters(
                    vision=OperationVisionParameters(
                        path=args.path,
                        color_model=args.vision_color_model,
                        high_noise_frac=args.vision_high_noise_frac,
                        image_format=args.vision_image_format,
                        n_steps=args.vision_steps,
                    )
                )

            case Modality.VISION_TEXT_TO_ANIMATION:
                parameters = OperationParameters(
                    vision=OperationVisionParameters(
                        path=args.path,
                        n_steps=args.vision_steps,
                        timestep_spacing=args.vision_timestep_spacing,
                        beta_schedule=args.vision_beta_schedule,
                        guidance_scale=args.vision_guidance_scale,
                    )
                )

            case Modality.VISION_TEXT_TO_VIDEO:
                parameters = OperationParameters(
                    vision=OperationVisionParameters(
                        path=args.path,
                        reference_path=getattr(
                            args, "vision_reference_path", None
                        ),
                        negative_prompt=getattr(
                            args, "vision_negative_prompt", None
                        ),
                        width=getattr(args, "vision_width", None),
                        height=getattr(args, "vision_height", None),
                        downscale=getattr(args, "vision_downscale", None),
                        frames=getattr(args, "vision_frames", None),
                        denoise_strength=getattr(
                            args, "vision_denoise_strength", None
                        ),
                        n_steps=getattr(args, "vision_steps", None),
                        inference_steps=getattr(
                            args, "vision_inference_steps", None
                        ),
                        decode_timestep=getattr(
                            args, "vision_decode_timestep", None
                        ),
                        noise_scale=getattr(args, "vision_noise_scale", None),
                        frames_per_second=getattr(args, "vision_fps", None),
                    )
                )

            case Modality.VISION_SEMANTIC_SEGMENTATION:
                parameters = OperationParameters(
                    vision=OperationVisionParameters(
                        path=args.path,
                    )
                )

            case _:
                parameters = None

        operation = Operation(
            generation_settings=settings,
            input=input_string,
            modality=modality,
            parameters=parameters,
            requires_input=requires_input,
        )

        return operation

    def get_engine_settings(
        self,
        engine_uri: EngineUri,
        settings: dict | None = None,
        modality: Modality | None = None,
    ) -> TransformerEngineSettings:
        engine_settings_args = settings or {}

        if modality != Modality.EMBEDDING and not engine_uri.is_local:
            token = None
            if engine_uri.password and engine_uri.user:
                if engine_uri.user == "secret":
                    token = self._secrets.read(engine_uri.password)
                else:
                    token = None
            elif engine_uri.user:
                token = engine_uri.user

            if token:
                engine_settings_args.update(access_token=token)

        engine_settings = TransformerEngineSettings(**engine_settings_args)
        return engine_settings

    def load(
        self,
        engine_uri: EngineUri,
        modality: Modality = Modality.TEXT_GENERATION,
        *args,
        attention: AttentionImplementation | None = None,
        base_url: str | None = None,
        device: str | None = None,
        disable_loading_progress_bar: bool = False,
        loader_class: TextGenerationLoaderClass | None = "auto",
        backend: Backend = Backend.TRANSFORMERS,
        low_cpu_mem_usage: bool = False,
        parallel: ParallelStrategy | None = None,
        quiet: bool = False,
        output_hidden_states: bool | None = None,
        base_model_id: str | None = None,
        checkpoint: str | None = None,
        refiner_model_id: str | None = None,
        upsampler_model_id: str | None = None,
        revision: str | None = None,
        special_tokens: list[str] | None = None,
        subfolder: str | None = None,
        tokenizer: str | None = None,
        tokenizer_subfolder: str | None = None,
        tokens: list[str] | None = None,
        trust_remote_code: bool | None = None,
        weight_type: WeightType = "auto",
    ) -> ModelType:
        engine_settings_args = dict(
            base_url=base_url,
            cache_dir=self._hub.cache_dir,
            device=device,
            disable_loading_progress_bar=quiet or disable_loading_progress_bar,
            low_cpu_mem_usage=low_cpu_mem_usage,
            loader_class=loader_class,
            backend=backend,
            parallel=parallel,
            base_model_id=base_model_id or None,
            checkpoint=checkpoint or None,
            refiner_model_id=refiner_model_id or None,
            upsampler_model_id=upsampler_model_id or None,
            revision=revision,
            special_tokens=special_tokens or None,
            subfolder=subfolder or None,
            tokenizer_name_or_path=tokenizer,
            tokenizer_subfolder=tokenizer_subfolder or None,
            tokens=tokens or None,
            weight_type=weight_type,
        )

        if output_hidden_states is not None:
            engine_settings_args["output_hidden_states"] = output_hidden_states

        if modality != Modality.EMBEDDING:
            engine_settings_args.update(
                attention=attention or None,
                trust_remote_code=trust_remote_code or None,
            )

        engine_settings = self.get_engine_settings(
            engine_uri,
            engine_settings_args,
            modality=modality,
        )
        return self.load_engine(engine_uri, engine_settings, modality)

    def load_engine(
        self,
        engine_uri: EngineUri,
        engine_settings: TransformerEngineSettings,
        modality: Modality = Modality.TEXT_GENERATION,
    ) -> ModelType:
        assert isinstance(engine_uri, EngineUri)
        model_load_args = dict(
            model_id=engine_uri.model_id,
            settings=engine_settings,
            logger=self._logger,
        )

        # Load local model, or lazy-import per vendor
        if engine_uri.is_local:
            match modality:
                case Modality.EMBEDDING:
                    model = SentenceTransformerModel(**model_load_args)
                case Modality.AUDIO_CLASSIFICATION:
                    model = AudioClassificationModel(**model_load_args)
                case Modality.AUDIO_SPEECH_RECOGNITION:
                    model = SpeechRecognitionModel(**model_load_args)
                case Modality.AUDIO_TEXT_TO_SPEECH:
                    model = TextToSpeechModel(**model_load_args)
                case Modality.AUDIO_GENERATION:
                    model = AudioGenerationModel(**model_load_args)
                case Modality.VISION_OBJECT_DETECTION:
                    model = ObjectDetectionModel(**model_load_args)
                case Modality.VISION_IMAGE_CLASSIFICATION:
                    model = ImageClassificationModel(**model_load_args)
                case Modality.VISION_IMAGE_TO_TEXT:
                    model = ImageToTextModel(**model_load_args)
                case Modality.VISION_IMAGE_TEXT_TO_TEXT:
                    model = ImageTextToTextModel(**model_load_args)
                case Modality.VISION_ENCODER_DECODER:
                    model = VisionEncoderDecoderModel(**model_load_args)
                case Modality.VISION_TEXT_TO_IMAGE:
                    model = TextToImageModel(**model_load_args)
                case Modality.VISION_TEXT_TO_ANIMATION:
                    model = TextToAnimationModel(**model_load_args)
                case Modality.VISION_TEXT_TO_VIDEO:
                    model = TextToVideoModel(**model_load_args)
                case Modality.VISION_SEMANTIC_SEGMENTATION:
                    model = SemanticSegmentationModel(**model_load_args)
                case Modality.TEXT_QUESTION_ANSWERING:
                    model = QuestionAnsweringModel(**model_load_args)
                case Modality.TEXT_SEQUENCE_CLASSIFICATION:
                    model = SequenceClassificationModel(**model_load_args)
                case Modality.TEXT_SEQUENCE_TO_SEQUENCE:
                    model = SequenceToSequenceModel(**model_load_args)
                case Modality.TEXT_TRANSLATION:
                    model = TranslationModel(**model_load_args)
                case Modality.TEXT_TOKEN_CLASSIFICATION:
                    model = TokenClassificationModel(**model_load_args)
                case _:
                    match engine_settings.backend:
                        case Backend.MLXLM:
                            from ..model.nlp.text.mlxlm import MlxLmModel

                            model = MlxLmModel(**model_load_args)
                        case Backend.VLLM:
                            from ..model.nlp.text.vllm import VllmModel

                            model = VllmModel(**model_load_args)
                        case _:
                            model = TextGenerationModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "openai"
        ):
            from ..model.nlp.text.vendor.openai import OpenAIModel

            model = OpenAIModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "openrouter"
        ):
            from ..model.nlp.text.vendor.openrouter import OpenRouterModel

            model = OpenRouterModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "anyscale"
        ):
            from ..model.nlp.text.vendor.anyscale import AnyScaleModel

            model = AnyScaleModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "together"
        ):
            from ..model.nlp.text.vendor.together import TogetherModel

            model = TogetherModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "deepseek"
        ):
            from ..model.nlp.text.vendor.deepseek import DeepSeekModel

            model = DeepSeekModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "deepinfra"
        ):
            from ..model.nlp.text.vendor.deepinfra import DeepInfraModel

            model = DeepInfraModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "groq"
        ):
            from ..model.nlp.text.vendor.groq import GroqModel

            model = GroqModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "ollama"
        ):
            from ..model.nlp.text.vendor.ollama import OllamaModel

            model = OllamaModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "huggingface"
        ):
            from ..model.nlp.text.vendor.huggingface import HuggingfaceModel

            model = HuggingfaceModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "hyperbolic"
        ):
            from ..model.nlp.text.vendor.hyperbolic import HyperbolicModel

            model = HyperbolicModel(**model_load_args)
        elif (
            modality == Modality.TEXT_GENERATION
            and engine_uri.vendor == "litellm"
        ):
            from ..model.nlp.text.vendor.litellm import LiteLLMModel

            model = LiteLLMModel(**model_load_args)
        else:
            raise NotImplementedError()

        self._stack.enter_context(model)
        return model

    @staticmethod
    def parse_uri(uri: str) -> EngineUri:
        parsed = urlparse(uri)
        if not parsed.scheme:
            uri = f"ai://{uri}"
            parsed = urlparse(uri)

        if parsed.scheme != "ai":
            raise ValueError(
                f"Invalid scheme {parsed.scheme!r}, expected 'ai'"
            )

        vendor = parsed.hostname
        if not vendor or vendor not in get_args(Vendor) or vendor == "local":
            vendor = None
        use_host = bool(vendor)
        path_prefixed = parsed.path.startswith("/")
        params = dict(parse_qsl(parsed.query))

        # urlparse() normalizes hostname to lowercase, so keep original case
        authority = parsed.netloc.rsplit("@", 1)[-1]
        hostname = authority.split(":", 1)[0]

        model_id = (
            hostname + ("/" if path_prefixed else "")
            if not vendor and hostname != "local"
            else ""
        ) + (parsed.path[1:] if path_prefixed else parsed.path)
        engine_uri = EngineUri(
            vendor=vendor,
            host=hostname if use_host else None,
            port=(parsed.port or None) if use_host else None,
            user=parsed.username or None,
            password=parsed.password or None,
            model_id=model_id,
            params=params,
        )
        return engine_uri
