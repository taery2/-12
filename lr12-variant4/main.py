"""ЛР 12, вариант 4. Раскраска графа: точный поиск, жадный алгоритм, локальный поиск."""
import random, time, statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def make_graph(n,p,seed):
    rng=random.Random(seed); adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if rng.random()<p: adj[i].add(j); adj[j].add(i)
    return adj

def valid(adj, colors):
    return all(colors[v]!=colors[u] for v in range(len(adj)) for u in adj[v])

def greedy_degree(adj):
    order=sorted(range(len(adj)),key=lambda v:(-len(adj[v]),v))
    colors=[-1]*len(adj)
    for v in order:
        used={colors[u] for u in adj[v] if colors[u]>=0}
        c=0
        while c in used: c+=1
        colors[v]=c
    return colors

def exact_coloring(adj):
    n=len(adj); order=sorted(range(n),key=lambda v:(-len(adj[v]),v))
    best=n; best_colors=None; colors=[-1]*n
    def search(pos,used):
        nonlocal best,best_colors
        if used>=best: return
        if pos==n:
            best=used; best_colors=colors[:]; return
        v=order[pos]
        forbidden={colors[u] for u in adj[v] if colors[u]>=0}
        for c in range(min(used+1,best)):
            if c not in forbidden:
                colors[v]=c; search(pos+1,max(used,c+1)); colors[v]=-1
    # Upper bound from greedy ensures pruning but must permit equal bound for solution.
    g=greedy_degree(adj); best=max(g)+1; best_colors=g[:]
    search(0,0)
    return best,best_colors

def local_recolor(adj, initial, max_steps=10000):
    colors=initial[:]; n=len(adj)
    # Try to eliminate the highest color by recoloring its vertices.
    for _ in range(max_steps):
        k=max(colors)+1
        if k<=1: break
        target=k-1; vertices=[v for v,c in enumerate(colors) if c==target]
        changed=False
        for v in vertices:
            used={colors[u] for u in adj[v]}
            for c in range(target):
                if c not in used:
                    colors[v]=c; changed=True; break
        if not changed: break
    return colors

if __name__=="__main__":
    print("ЛР 12. Булова Екатерина, БИ 2-1, вариант 4")
    print("n    точный оптимум  жадный  локальный")
    # М4: усреднённое отклонение эвристики от точного оптимума.
    for n in (6,7,8,9):
        dev_g=[]; dev_l=[]; opts=[]
        for seed in range(30):
            adj=make_graph(n,0.25,seed=seed+100*n)
            opt,_=exact_coloring(adj)
            opts.append(opt)
            g=greedy_degree(adj); l=local_recolor(adj,g)
            kg=max(g)+1; kl=max(l)+1
            dev_g.append((kg-opt)/opt*100)
            dev_l.append((kl-opt)/opt*100)
            assert valid(adj,g) and valid(adj,l)
        print(f"{n:<5}{statistics.mean(opts):<17.2f}{statistics.mean(dev_g):<8.2f}{statistics.mean(dev_l):.2f}")
        print(f"     среднее отклонение жадного: {statistics.mean(dev_g):.2f}%; локального: {statistics.mean(dev_l):.2f}%")

    # Большой граф n=200: только эвристики, точный перебор здесь нецелесообразен.
    adj=make_graph(200,0.12,seed=2026)
    t=time.perf_counter(); g=greedy_degree(adj); tg=time.perf_counter()-t
    t=time.perf_counter(); l=local_recolor(adj,g); tl=time.perf_counter()-t
    assert valid(adj,g) and valid(adj,l)
    print(f"\\nn=200: жадный={max(g)+1} цветов ({tg:.4f} c), локальный={max(l)+1} цветов ({tl:.4f} c)")
    plt.figure()
    ns=[6,7,8,9]
    # The table above is the measured quality; reproduce values deterministically for the plot.
    dg=[]
    for n in ns:
        vals=[]
        for seed in range(30):
            a=make_graph(n,0.25,seed=seed+100*n); opt,_=exact_coloring(a)
            vals.append((max(greedy_degree(a))+1-opt)/opt*100)
        dg.append(statistics.mean(vals))
    plt.plot(ns,dg,marker="o",label="Жадный алгоритм")
    plt.xlabel("Число вершин n"); plt.ylabel("Среднее отклонение, %")
    plt.title("ЛР 12. Качество эвристики раскраски"); plt.grid(True); plt.legend()
    plt.tight_layout(); plt.savefig("results/coloring_deviation.png",dpi=160)
