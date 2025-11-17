import sys
import os
import mysql.connector  # ✅ import corrigido

# ========= Config de conexão =========
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "301103021227-")
DB_NAME = os.getenv("DB_NAME", "projetobdd")

# ========= Utilitários =========
def pausar():
    input("\nPressione ENTER para continuar...")

def perguntar_opcao(msg, opcoes_validas):
    op = input(msg).strip()
    return op if op in opcoes_validas else None

def conectar(database: str = DB_NAME):
    return mysql.connector.connect(  # ✅ corrigido
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=database,
        autocommit=False
    )

def print_tabela(rows, header):
    if not rows:
        print("\n(nenhum registro)")
        return
    larg = [len(h) for h in header]
    for r in rows:
        for i, v in enumerate(r):
            larg[i] = max(larg[i], len(str(v)))
    linha = " | ".join(h.ljust(larg[i]) for i, h in enumerate(header))
    sep   = "-+-".join("-"*larg[i] for i in range(len(header)))
    print("\n" + linha); print(sep)
    for r in rows:
        print(" | ".join(str(r[i]).ljust(larg[i]) for i in range(len(header))))

# ========= Ações =========
def listar_produtos():
    try:
        conn = conectar(); cur = conn.cursor()

        # 1) Catálogo
        cur.execute("""
            SELECT p.id, p.nome, p.preco, p.quantidade_estoque
            FROM produto p
            ORDER BY p.nome
        """)
        cat = cur.fetchall()
        print("\nCATÁLOGO DE PRODUTOS")
        print_tabela(cat, ["ID","Nome","Preço","Estoque"])

        # 2) View 1
        try:
            cur.execute("SELECT * FROM vw_produtos_mais_vendidos")
            rows = cur.fetchall()
            if rows:
                header = [d[0] for d in cur.description]
                print("\nVIEW 1: PRODUTOS MAIS VENDIDOS")
                print_tabela(rows, header)
        except mysql.connector.Error:
            pass

        # 3) View 2
        try:
            cur.execute("SELECT * FROM vw_vendas_por_vendedor")
            rows = cur.fetchall()
            if rows:
                header = [d[0] for d in cur.description]
                print("\nVIEW 2: VENDAS POR VENDEDOR")
                print_tabela(rows, header)
        except mysql.connector.Error:
            pass

        # 4) View 3
        try:
            cur.execute("SELECT * FROM vw_frete_por_destino")
            rows = cur.fetchall()
            if rows:
                header = [d[0] for d in cur.description]
                print("\nVIEW 3: FRETE / ITENS POR DESTINO")
                print_tabela(rows, header)
        except mysql.connector.Error:
            pass

        conn.commit()
    except Exception as e:
        print("[ERRO] listar_produtos:", e)
    finally:
        try: cur.close(); conn.close()
        except: pass
    pausar()

def cadastrar_cliente():
    try:
        nome = input("Nome: ").strip()
        idade = int(input("Idade: ").strip())
        sexo = input("Sexo (M/F/O): ").strip().upper()
        nascimento = input("Nascimento (AAAA-MM-DD): ").strip()

        conn = conectar(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO cliente (nome, idade, sexo, data_nascimento)
            VALUES (%s,%s,%s,%s)
        """, (nome, idade, sexo, nascimento))
        conn.commit()
        print("✅ Cliente cadastrado.")
    except Exception as e:
        print("[ERRO] cadastrar_cliente:", e)
        try: conn.rollback()
        except: pass
    finally:
        try: cur.close(); conn.close()
        except: pass
    pausar()

def cadastrar_produto():
    try:
        nome = input("Nome do produto: ").strip()
        preco = float(input("Preço: ").strip())
        estoque = int(input("Estoque: ").strip())
        vendedor_id = int(input("Vendedor ID: ").strip())
        descricao = input("Descrição (opcional): ").strip() or "Produto cadastrado manualmente"
        observacoes = input("Observações (opcional): ").strip() or None

        conn = conectar(); cur = conn.cursor()

        cur.execute("SELECT id FROM vendedor WHERE id=%s", (vendedor_id,))
        if cur.fetchone() is None:
            print("⚠️ Vendedor não existe. Use um ID válido.")
            return

        cur.execute("""
            INSERT INTO produto (nome, descricao, quantidade_estoque, preco, observacoes, vendedor_id)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (nome, descricao, estoque, preco, observacoes, vendedor_id))
        conn.commit()
        print("✅ Produto cadastrado.")
    except Exception as e:
        print("[ERRO] cadastrar_produto:", e)
        try: conn.rollback()
        except: pass
    finally:
        try: cur.close(); conn.close()
        except: pass
    pausar()

def reajuste_salarial():
    try:
        tipo = input("Tipo/Cargo (ex.: 'Pleno', 'Sênior', ...): ").strip()
        percent = float(input("Percentual (ex.: 5 para 5%): ").strip())

        conn = conectar(); cur = conn.cursor()
        cur.callproc("reajuste_salarial", [tipo, percent])
        conn.commit()
        print("✅ Reajuste aplicado para", tipo)
    except Exception as e:
        print("[ERRO] reajuste_salarial:", e)
        try: conn.rollback()
        except: pass
    finally:
        try: cur.close(); conn.close()
        except: pass
    pausar()

def criar_bd():
    """Cria o banco e aplica todos os .sql, respeitando DELIMITER"""
    def parse_sql_file(path):
        commands = []
        if not os.path.exists(path):
            return commands
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        delim = ";"
        buf = []
        def flush():
            stmt = "".join(buf).strip()
            if stmt:
                commands.append(stmt)
            buf.clear()
        for raw in lines:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if stripped.startswith("--"): continue
            if stripped.startswith("/*") and stripped.endswith("*/"): continue
            if stripped.upper().startswith("DELIMITER "):
                delim = stripped.split(None,1)[1].strip()
                continue
            if buf: buf.append("\n")
            buf.append(line)
            if delim and stripped.endswith(delim):
                if buf[-1].endswith(delim):
                    buf[-1] = buf[-1][:-len(delim)]
                flush()
        flush()
        return commands

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        arquivos = ["projetobdd.sql","functions.sql","procedures.sql","triggers.sql","views.sql","usuarios.sql"]

        conn = mysql.connector.connect(  # ✅ corrigido
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, autocommit=False
        )
        cur = conn.cursor()

        print(f"🗑️  Drop do banco {DB_NAME} se existir...")
        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        conn.commit()

        for fname in arquivos:
            path = os.path.join(base_dir, fname)
            if not os.path.exists(path): continue
            print(f"-> Executando {fname}")
            cmds = parse_sql_file(path)
            for cmd in cmds:
                try:
                    if cmd.strip():
                        cur.execute(cmd)
                except mysql.connector.Error as e:
                    print(f"⚠️ Erro executando comando em {fname}: {e}")
                    print(f"   Comando (início): {cmd[:120]}...")
            conn.commit()

        cur.execute("SHOW DATABASES")
        bancos = [r[0] for r in cur.fetchall()]
        if DB_NAME not in bancos:
            print(f"❌ O banco {DB_NAME} não foi criado. Verifique o projetobdd.sql.")
            return
        cur.execute(f"USE {DB_NAME}")
        cur.execute("SHOW TABLES")
        tabelas = [r[0] for r in cur.fetchall()]
        print("✅ Banco criado e objetos aplicados.")
        print("📋 Tabelas criadas:", ", ".join(tabelas) if tabelas else "(nenhuma)")

    except Exception as e:
        print("[ERRO] criar_bd:", e)
        try: conn.rollback()
        except: pass
    finally:
        try: cur.close(); conn.close()
        except: pass
    pausar()

def destruir_bd():
    try:
        conn = mysql.connector.connect(  # ✅ corrigido
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, autocommit=True
        )
        cur = conn.cursor()
        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cur.execute("SHOW DATABASES")
        bancos = [r[0] for r in cur.fetchall()]
        if DB_NAME in bancos:
            print(f"❌ Não foi possível destruir {DB_NAME}.")
        else:
            print(f"🗑️  Banco {DB_NAME} destruído.")
    except Exception as e:
        print("[ERRO] destruir_bd:", e)
    finally:
        try: cur.close(); conn.close()
        except: pass
    pausar()

# ========= Menus =========
def menu_cliente():
    while True:
        print("\n=== MENU: CLIENTE ===")
        print("[1] Listar produtos")
        print("[0] Voltar")
        op = perguntar_opcao("Escolha: ", {"1","0"})
        if op == "1": listar_produtos()
        elif op == "0": return

def menu_funcionario():
    while True:
        print("\n=== MENU: FUNCIONÁRIO ===")
        print("[1] Cadastrar cliente")
        print("[2] Cadastrar produto")
        print("[3] Listar produtos")
        print("[0] Voltar")
        op = perguntar_opcao("Escolha: ", {"1","2","3","0"})
        if op == "1": cadastrar_cliente()
        elif op == "2": cadastrar_produto()
        elif op == "3": listar_produtos()
        elif op == "0": return

def menu_gerente():
    while True:
        print("\n=== MENU: GERENTE ===")
        print("[1] Reajuste salarial")
        print("[2] Cadastrar cliente")
        print("[3] Cadastrar produto")
        print("[4] Listar produtos")
        print("[0] Voltar")
        op = perguntar_opcao("Escolha: ", {"1","2","3","4","0"})
        if op == "1": reajuste_salarial()
        elif op == "2": cadastrar_cliente()
        elif op == "3": cadastrar_produto()
        elif op == "4": listar_produtos()
        elif op == "0": return

def menu_administrador():
    while True:
        print("\n=== MENU: ADMINISTRADOR ===")
        print("[1] Criar/Resetar banco de dados")
        print("[2] Destruir banco de dados")
        print("[3] Cadastrar cliente")
        print("[4] Cadastrar produto")
        print("[5] Listar produtos")
        print("[0] Voltar")
        op = perguntar_opcao("Escolha: ", {"1","2","3","4","5","0"})
        if op == "1": criar_bd()
        elif op == "2": destruir_bd()
        elif op == "3": cadastrar_cliente()
        elif op == "4": cadastrar_produto()
        elif op == "5": listar_produtos()
        elif op == "0": return

# ========= Menu principal =========
def menu_principal():
    while True:
        print("\n=== SISTEMA — ESCOLHA SEU PERFIL ===")
        print("[1] Cliente")
        print("[2] Funcionário")
        print("[3] Gerente")
        print("[4] Administrador")
        print("[0] Sair")
        op = perguntar_opcao("Escolha: ", {"1","2","3","4","0"})
        if op == "1": menu_cliente()
        elif op == "2": menu_funcionario()
        elif op == "3": menu_gerente()
        elif op == "4": menu_administrador()
        elif op == "0":
            print("Saindo...")
            sys.exit(0)

if __name__ == "__main__":
    menu_principal()
