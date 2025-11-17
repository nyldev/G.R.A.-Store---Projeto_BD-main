import os
import random
import datetime as dt
import mysql.connector as mysql

# ---- Config de conexão ----
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "301103021227-")
DB_NAME = os.getenv("DB_NAME", "projetobdd")

def conectar():
    return mysql.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, autocommit=False
    )

# ---- Helpers simples ----
def get_scalar(cur, sql, args=()):
    cur.execute(sql, args)
    row = cur.fetchone()
    return row[0] if row else None

def ensure_cargos(cur):

    """Insere 5 cargos se ainda não existirem."""
    cargos = ["Júnior", "Pleno", "Sênior", "Gerente", "Diretor"]
    cur.execute("SELECT COUNT(*) FROM cargo")
    count = cur.fetchone()[0]
    if count < 5:
        cur.execute("SELECT nome FROM cargo")
        existentes = {r[0] for r in cur.fetchall()}
        faltantes = [c for c in cargos if c not in existentes]
        if faltantes:
            cur.executemany("INSERT INTO cargo (nome) VALUES (%s)", [(c,) for c in faltantes])
    print("✅ Cargos ok (>=5).")

def ensure_vendedores(cur):
    """Garante ao menos 10 vendedores para referenciar nos produtos."""
    qtd = get_scalar(cur, "SELECT COUNT(*) FROM vendedor")
    if qtd and qtd >= 10:
        print("✅ Vendedores ok (>=10).")
        return

    # mapeia cargos por nome -> id
    cur.execute("SELECT id, nome FROM cargo")
    mapa_cargo = {nome: _id for _id, nome in cur.fetchall()}
    def cid(nome): return mapa_cargo.get(nome)

    # agora cada vendedor tem: nome, causa_social, tipo, nota, salario, cargo_id
    vendedores = [
        ("Ana Lima",    "ME",   "Júnior",  3.8, 2500.00, cid("Júnior")),
        ("Bruno Paz",   "ME",   "Júnior",  4.1, 2700.00, cid("Júnior")),
        ("Carla Luz",   "LTDA", "Pleno",   4.2, 3500.00, cid("Pleno")),
        ("Davi Araujo", "LTDA", "Pleno",   4.0, 3400.00, cid("Pleno")),
        ("Eva Reis",    "SA",   "Sênior",  4.5, 5200.00, cid("Sênior")),
        ("Fábio Nery",  "SA",   "Sênior",  4.6, 5400.00, cid("Sênior")),
        ("Gabi Tavares","EPP",  "Gerente", 4.3, 6500.00, cid("Gerente")),
        ("Hugo Curi",   "EPP",  "Gerente", 4.4, 6600.00, cid("Gerente")),
        ("Iris Melo",   "SA",   "Diretor", 4.8, 9000.00, cid("Diretor")),
        ("João Lara",   "SA",   "Diretor", 4.7, 8800.00, cid("Diretor")),
    ]

    cur.execute("SELECT nome FROM vendedor")
    existentes = {r[0] for r in cur.fetchall()}
    novos = [v for v in vendedores if v[0] not in existentes]

    if novos:
        cur.executemany("""
            INSERT INTO vendedor (nome, causa_social, tipo, nota, salario, cargo_id)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, novos)

    print("✅ Vendedores prontos (>=10).")


def seed_clientes(cur, alvo=100):

    """Gera clientes 'Cliente 001'.. até atingir 100 no total."""
    total = get_scalar(cur, "SELECT COUNT(*) FROM cliente")
    if total is None: total = 0
    if total >= alvo:
        print("✅ Clientes ok (>=100).")
        return

    cur.execute("SELECT nome FROM cliente WHERE nome LIKE 'Cliente %'")
    existentes = {r[0] for r in cur.fetchall()}
    hoje = dt.date.today()
    rows = []
    for n in range(1, alvo + 1):
        nome = f"Cliente {n:03d}"
        if nome in existentes:
            continue
        idade = 18 + (n % 43)
        sexo = ["M", "F", "O"][n % 3]
        nasc = hoje - dt.timedelta(days=365 * idade + (n % 365))
        rows.append((nome, idade, sexo, nasc))
    if rows:
        cur.executemany(
            "INSERT INTO cliente (nome, idade, sexo, data_nascimento) VALUES (%s,%s,%s,%s)",
            rows
        )
    print("✅ Clientes prontos (>=100).")


def seed_produtos_mma(cur, alvo=20):

    """
    Cria até 20 produtos de MMA (evita duplicar por nome).
    Distribui entre os vendedores existentes.
    """

    total = get_scalar(cur, "SELECT COUNT(*) FROM produto")
    if total is None: total = 0
    if total >= alvo:
        print("✅ Produtos ok (>=20).")
        return

    cur.execute("SELECT id FROM vendedor ORDER BY id")
    vendedores = [r[0] for r in cur.fetchall()]
    if not vendedores:
        raise RuntimeError("Não há vendedores para vincular aos produtos.")

    cur.execute("SELECT nome FROM produto")
    existentes = {r[0] for r in cur.fetchall()}

    mma_catalog = [
        ("Luva MMA Pro 10oz",      "Luva de combate 10oz, PU premium",             (25,120), 219.90),
        ("Luva MMA Pro 12oz",      "Luva de combate 12oz, PU premium",             (25,120), 229.90),
        ("Luva Sparring 16oz",     "Luva sparring 16oz acolchoamento duplo",       (20,90),  269.90),
        ("Luvas de Saco 12oz",     "Luva para saco 12oz, reforço de punho",         (20,80),  179.90),
        ("Caneleira Pro",          "Caneleira com velcro duplo, alto impacto",     (25,90),  199.90),
        ("Protetor Bucal Duplo",   "Bocal duplo termoajustável",                    (40,150),  39.90),
        ("Protetor Genital",       "Coquilha anatômica com ajuste elástico",        (25,80),   69.90),
        ("Bandagem Elástica 3m",   "Bandagem elástica 3 metros",                    (60,200),  24.90),
        ("Bandagem Elástica 4,5m", "Bandagem elástica 4,5 metros",                  (60,200),  29.90),
        ("Corda de Pular Speed",   "Corda speed com rolamento metálico",            (30,120),  49.90),
        ("Shorts de Compressão",   "Shorts de compressão para grappling",           (25,90),   89.90),
        ("Shorts Muay Thai",       "Shorts tecido leve",                            (25,90),  119.90),
        ("Rashguard Manga Curta",  "Rashguard anti-fúngica, proteção UV",           (20,80),  139.90),
        ("Rashguard Manga Longa",  "Rashguard manga longa",                         (20,80),  149.90),
        ("Focus Mitt Curvo",       "Manopla curvada PU, par",                       (15,60),  189.90),
        ("Thai Pad",               "Apoio de chute couro sintético, unidade",       (10,50),  279.90),
        ("Capacete Sparring",      "Capacete com proteção zigomática",              (10,50),  299.90),
        ("Mochila de Treino 40L",  "Mochila ventilada com compartimento úmido",     (10,40),  219.90),
        ("Saco de Pancada 1,50m",  "Saco 1,50m enchimento têxtil",                  (5,25),   399.90),
        ("Mitts de Agilidade",     "Mitts leves para precisão, par",                (15,60),  129.90),
    ]

    rows = []
    idx_vend = 0
    for nome, descricao, faixa_estoque, preco in mma_catalog:
        if len(rows) + total >= alvo:
            break
        if nome in existentes:
            continue
        est_min, est_max = faixa_estoque
        estoque = random.randint(est_min, est_max)
        vendedor_id = vendedores[idx_vend % len(vendedores)]
        idx_vend += 1
        rows.append((nome, descricao, estoque, float(preco), None, vendedor_id))

    if rows:
        cur.executemany("""
            INSERT INTO produto (nome, descricao, quantidade_estoque, preco, observacoes, vendedor_id)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, rows)

    print("✅ Produtos MMA prontos (>=20).")

def main():
    print("== Seed nativos: 5 cargos, 10 vendedores (se faltar), 100 clientes, 20 produtos MMA ==")
    conn = conectar()
    cur = conn.cursor()
    try:
        ensure_cargos(cur)
        ensure_vendedores(cur)
        seed_clientes(cur, 100)
        seed_produtos_mma(cur, 20)   # <--- aqui trocamos para os itens de MMA
        conn.commit()
        print("\n🌱 Seed concluído.")
    except Exception as e:
        conn.rollback()
        print("ERRO:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
