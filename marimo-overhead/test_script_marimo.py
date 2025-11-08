import marimo

__generated_with = "0.9.0"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    # Simple computation
    result = sum(range(1000))
    print(f"Result: {result}")
    return result,


if __name__ == "__main__":
    app.run()
