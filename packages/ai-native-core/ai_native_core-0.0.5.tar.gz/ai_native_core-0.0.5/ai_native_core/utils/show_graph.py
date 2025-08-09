def show_graph(graph):
    png_bytes = graph.get_graph().draw_mermaid_png()
    # save to .png
    with open("./graph.png", "wb") as f:
        f.write(png_bytes)
