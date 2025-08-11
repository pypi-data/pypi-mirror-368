from time import perf_counter

from rich import print as rprint

from wujing.llm.llm_call import llm_call


def test_llm_call_cache(volces, messages, response_model):
    common_params = {
        "api_key": volces[1],
        "api_base": volces[0],
        "model": volces[2],
        "messages": messages,
        "protocol": "openai",
        "cache_enabled": True,
    }

    start_time = perf_counter()
    llm_call(**common_params)
    first_call_elapsed = perf_counter() - start_time

    start_time = perf_counter()
    llm_call(**common_params)
    second_call_elapsed = perf_counter() - start_time

    assert second_call_elapsed < first_call_elapsed, (
        f"缓存未命中，第二次调用时间: {second_call_elapsed:.4f}s vs 第一次调用时间: {first_call_elapsed:.4f}s"
    )


def test_llm_call_with_openai_prompt(volces, messages, response_model):
    resp = llm_call(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
        protocol="openai",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
        response_model=response_model,
        protocol="openai",
        formatter="prompt",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_openai_vllm(vllm, messages, response_model, context):
    resp = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        protocol="openai",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        response_model=response_model,
        context=context,
        protocol="openai",
        formatter="vllm",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_openai_vllm_v2(vllm, messages, response_model_with_root_model, context):
    resp = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        protocol="openai",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        response_model=response_model_with_root_model,
        context=context,
        protocol="openai",
        formatter="vllm",
        cache_enabled=False,
    )
    rprint(f"{response_model_with_root_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_azure(azure, messages, response_model):
    resp = llm_call(
        api_key=azure[1],
        api_version=azure[2],
        api_base=azure[0],
        model=azure[3],
        messages=messages,
        protocol="azure",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=azure[1],
        api_version=azure[2],
        api_base=azure[0],
        model=azure[3],
        messages=messages,
        response_model=response_model,
        protocol="azure",
        formatter="azure",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")
