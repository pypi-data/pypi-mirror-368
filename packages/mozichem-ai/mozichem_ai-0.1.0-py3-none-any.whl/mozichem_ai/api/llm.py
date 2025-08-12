# import libs
import logging
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
# local imports
from ..llms import LlmManager
from ..config import llm_providers
from ..models import LlmConfig


# NOTE: logger
logger = logging.getLogger(__name__)

# SECTION: api router
llm_router = APIRouter()

# SECTION: routes


@llm_router.post("/llm/ping", response_model=bool)
async def ping_llm(
    request: LlmConfig
):
    """
    Initialize the LLM with the given parameters.

    Parameters
    ----------
    request : LlmConfig
        Configuration for the LLM, including:
    - model_provider: str
        The provider of the LLM model (e.g., "openai", "google").
    - model_name: str
        The name of the LLM model to use (e.g., "gpt-3.5-turbo", "gemini-1.5-pro").
    - temperature: float
        The temperature for the LLM model, controlling randomness in responses.
    - max_tokens: int
        The maximum number of tokens for the LLM model response.
    """
    try:
        # SECTION: extract parameters
        model_provider = request.model_provider
        model_name = request.model_name
        temperature = request.temperature
        max_tokens = request.max_tokens

        logger.info(
            f"Initializing LLM with provider: {model_provider}, model: {model_name}, temperature: {temperature}, max_tokens: {max_tokens}")

        # NOTE: add kwargs for LLM manager
        kwargs = {
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # SECTION: validate inputs
        if not model_provider or not model_name:
            raise HTTPException(
                status_code=400, detail="Model provider and name must be provided.")

        # NOTE: check if model provider is supported
        if model_provider not in llm_providers:
            raise HTTPException(
                status_code=400, detail=f"Unsupported model provider: {model_provider}. Supported providers are: {', '.join(llm_providers)}.")

        # SECTION: init llm manager
        llm_manager = LlmManager(
            model_provider=model_provider,
            model_name=model_name
        )

        # SECTION: ping the model
        response = llm_manager.ping()

        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))
