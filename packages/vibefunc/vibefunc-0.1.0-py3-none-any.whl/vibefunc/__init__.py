import hashlib
import inspect
import os
from functools import wraps

from openai import OpenAI


def vibefunc(
    model="gpt-4.1-mini",
    mode="serious",
    save_money=True,
    debug=False,
    base_url=None,
):
    """
    Decorator that generates a function body using an LLM based on its signature and docstring.

    Args:
        model (str): OpenAI model name, e.g. "gpt-4o-mini".
        mode (str): "serious" for correct implementation, "chaotic" for creative/funny code.
        base_url (str, optional): Custom base URL for OpenAI API. Defaults to None.
        save_money (bool): If True, saves the generated function body to a cache file to avoid repeated API calls.
        debug (bool): If True, prints debug information.
    """
    if base_url is None:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    else:
        client = OpenAI(
            base_url=base_url,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    if save_money:
        CACHE_DIR = ".vibefunc_cache"
        os.makedirs(CACHE_DIR, exist_ok=True)
        print(
            f"Cache directory created/used at {CACHE_DIR}. Cached function bodies will be saved here for saving money."
        )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            doc = inspect.getdoc(func) or ""
            ann = func.__annotations__

            cache_file = None

            # if cache file exists, read from it
            if save_money:
                # set cache key based hash(func name, signature, docstring, and annotations)
                cache_key = hashlib.md5(
                    (func.__name__ + str(sig) + doc + str(ann)).encode()
                ).hexdigest()
                cache_file = os.path.join(CACHE_DIR, cache_key + ".py")
                if os.path.exists(cache_file):
                    with open(cache_file, "r", encoding="utf-8") as f:
                        code_body = f.read()
            else:
                # let's fuxxing vibing
                if mode == "serious":
                    prompt = f"""
                        You are a Python expert. Write ONLY the function body (no def line, just plain textm, no markdown fences) for:
                        Function name: {func.__name__}
                        Signature: {func.__name__}{sig}
                        Annotations: {ann}
                        Docstring: {doc}
                        Make sure the code runs correctly and returns a valid result.
                        """
                elif mode == "chaotic":
                    prompt = f"""
                        You are a humorous and creative Python coder. Write ONLY the function body (no def line, just plain textm, no markdown fences) for:
                        Function name: {func.__name__}
                        Signature: {func.__name__}{sig}
                        Annotations: {ann}
                        Docstring: {doc}
                        Make it funny, unexpected, but still runnable Python code.
                        """
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )
                code_body = resp.choices[0].message.content.strip()

            if debug:
                print(code_body)

            # generate the function source code
            func_src = f"def _gen_func{sig}:\n"
            for line in code_body.split("\n"):
                func_src += "    " + line + "\n"

            local_env = {}
            try:
                exec(func_src, globals(), local_env)
                result = local_env["_gen_func"](*args, **kwargs)

                if save_money:
                    if os.path.exists(cache_file):
                        with open(cache_file, "w", encoding="utf-8") as f:
                            f.write(code_body)

                return result
            except Exception as e:
                if save_money:
                    if os.path.exists(cache_file):
                        os.remove(cache_file)
                raise e

        return wrapper

    return decorator


# @vibefunc
# def sort(a: list):
#     """Sort the list in ascending order and print the sorted list."""
#     ...
