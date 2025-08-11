from vibefunc import vibefunc


@vibefunc(
    save_money=False,
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-4o-mini",
    # mode="chaotic",
    # debug=True,
)
def sort(a: list):
    """Sort the list in ascending order and print the sorted list."""
    ...


sort([1, 222, 3333, 4, 45634, 1314235, 233])
