import sys
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyArrowPatch

# === Definición del DFA ===
states = {"q0", "q1", "q2", "q3", "q4"}
alphabet = {"a", "b"}
delta = {
    ("q0", "a"): "q1",
    ("q1", "a"): "q4",
    ("q1", "b"): "q4",
    ("q2", "a"): "q0",
    ("q2", "b"): "q1",
    ("q3", "b"): "q2",
    ("q4", "a"): "q4",
    ("q4", "b"): "q4"
}

q0, F = "q0", {"q4"}

# === Simulación ===
def run(s):
    q, steps = q0, [q0]
    for i, ch in enumerate(s):
        if ch not in alphabet:
            return steps, False, f"Símbolo '{ch}' no pertenece al alfabeto {alphabet}"
        if (q, ch) not in delta:
            return steps, False, f"Sin transición desde {q} con '{ch}' en pos {i}"
        q = delta[(q, ch)]
        steps.append(q)
    
    ok = steps[-1] in F
    msg = "ACEPTA" if ok else f"RECHAZA (terminó en estado no final {steps[-1]})"
    return steps, ok, msg

# === Grafo y layout ===
G = nx.DiGraph()
G.add_nodes_from(states)

# Agrupar transiciones con mismo origen y destino (ej. 'a' y 'b' -> 'a, b')
grouped_edges = {}
for (u, sym), v in delta.items():
    grouped_edges.setdefault((u, v), []).append(sym)

for (u, v), syms in grouped_edges.items():
    G.add_edge(u, v, label=", ".join(sorted(syms)))

# Layout fijo y bien distribuido
pos = nx.spring_layout(G, seed=42, k=1.5)

def _mid(p1, p2, offset=0.12):
    (x1, y1), (x2, y2) = p1, p2
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = (dx**2 + dy**2)**0.5 or 1
    return mx - offset * dy / L, my + offset * dx / L

# === Dibujo por paso ===
def draw_step(current, idx, sym=None, status_color=None, extra_title=""):
    plt.clf()
    ax = plt.gca()
    nodes = list(G.nodes())

    # Colores de los nodos
    node_colors = []
    for n in nodes:
        if n == current:
            node_colors.append(status_color if status_color else "#FFD166") # Amarillo activo
        else:
            node_colors.append("#E0E1DD") # Gris claro inactivo

    # Dibujar nodos principales
    nx.draw_networkx_nodes(
        G, pos, nodelist=nodes, node_color=node_colors,
        node_size=[1100 if n == current else 850 for n in nodes],
        edgecolors="black", linewidths=1.5
    )

    # Doble círculo para estados finales (F)
    final_nodes = [n for n in nodes if n in F]
    nx.draw_networkx_nodes(
        G, pos, nodelist=final_nodes, node_color="none",
        node_size=[750 if n == current else 550 for n in final_nodes],
        edgecolors="black", linewidths=1.5
    )

    nx.draw_networkx_labels(G, pos, font_weight="bold", font_size=11)

    # Flecha de estado inicial (q0)
    x0, y0 = pos[q0]
    ax.annotate(
        "", xy=(x0 - 0.13, y0), xytext=(x0 - 0.45, y0),
        arrowprops=dict(arrowstyle="-|>", lw=2, color="black", mutation_scale=18)
    )

    # Dibujar aristas y etiquetas
    for u, v, d in G.edges(data=True):
        if u == v:
            # Auto-bucle (self-loop)
            x, y = pos[u]
            loop = FancyArrowPatch(
                (x - 0.08, y + 0.08), (x + 0.08, y + 0.08),
                connectionstyle="arc3,rad=-2.2",
                arrowstyle='-|>', mutation_scale=16, linewidth=1.3,
                color="#333333", zorder=5, clip_on=False
            )
            ax.add_patch(loop)
            plt.text(x, y + 0.32, d["label"], fontsize=10, fontweight="bold",
                     ha="center", va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
        else:
            # Curvatura si existe arista inversa (v -> u)
            rad = 0.18 if G.has_edge(v, u) else 0.05
            nx.draw_networkx_edges(
                G, pos, edgelist=[(u, v)], connectionstyle=f"arc3,rad={rad}",
                arrows=True, arrowstyle='-|>', arrowsize=18, edge_color="#333333",
                node_size=950, width=1.3
            )
            lx, ly = _mid(pos[u], pos[v], offset=0.14 if G.has_edge(v, u) else 0.06)
            plt.text(lx, ly, d["label"], fontsize=10, fontweight="bold",
                     ha="center", va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

    # Ajustar márgenes para que no se corten los bucles
    ax.margins(0.25)
    plt.axis('off')
    
    titulo = f"Paso {idx}: Estado '{current}'"
    if sym:
        titulo += f" | Leyendo '{sym}'"
    if extra_title:
        titulo += f"\n{extra_title}"
        
    plt.title(titulo, fontsize=12, fontweight="bold", pad=15)
    plt.pause(0.9)

# === Main ===
if __name__ == '__main__':
    s = sys.argv[1] if len(sys.argv) > 1 else input("Cadena (a/b): ").strip()
    steps, ok, msg = run(s)
    print(msg)

    plt.figure(figsize=(8, 6))
    plt.ion()
    
    # Paso 0 (estado inicial)
    is_last_at_start = (len(steps) == 1)
    color_0 = ("#06D6A0" if ok else "#EF476F") if is_last_at_start else None
    draw_step(steps[0], 0, status_color=color_0, extra_title=(msg if is_last_at_start else ""))

    # Pasos siguientes
    for i in range(1, len(steps)):
        is_last = (i == len(steps) - 1)
        final_color = ("#06D6A0" if ok else "#EF476F") if is_last else None
        extra = msg if is_last else ""
        draw_step(steps[i], i, sym=s[i - 1], status_color=final_color, extra_title=extra)

    plt.ioff()
    plt.show()