import sqlite3
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('crm_empresa_pro.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                empresa TEXT,
                cnpj TEXT,
                telefone TEXT,
                email TEXT,
                vendedor TEXT DEFAULT 'Aquiles',
                status TEXT DEFAULT 'Novo Lead',
                temperatura TEXT DEFAULT 'Morno',
                valor REAL DEFAULT 0.0,
                tipo_pagamento TEXT DEFAULT 'À Vista',
                parcelas INTEGER DEFAULT 1,
                valor_pago REAL DEFAULT 0.0,
                historico TEXT DEFAULT 'Conta criada no CRM.',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                remetente TEXT DEFAULT 'Atendente',
                mensagem TEXT NOT NULL,
                data_msg TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(cliente_id) REFERENCES clientes(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                assunto TEXT NOT NULL,
                descricao TEXT,
                prioridade TEXT DEFAULT 'Normal',
                status_ticket TEXT DEFAULT 'Aberto',
                data_ticket TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(cliente_id) REFERENCES clientes(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                tipo TEXT DEFAULT 'Operacional'
            )
        ''')
        conn.commit()

init_db()

HTML_CRM = r'''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CONVERIS ENTERPRISE - Central de Chat</title>
    <style>
        :root { 
            --bg: #0b0f19; --card-bg: #111827; --gold: #d4af37; --whatsapp: #25d366; 
            --text-light: #e5e7eb; --text-muted: #9ca3af; --border: #1f2937;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: var(--bg); color: var(--text-light); }
        header { background: #030712; border-bottom: 2px solid var(--gold); padding: 12px 15px; text-align: center; }
        .logo-box { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 8px; }
        .logo-symbol { font-size: 24px; color: var(--gold); }
        .logo-title h1 { margin: 0; font-size: 18px; color: #fff; letter-spacing: 1px; }
        .logo-title small { color: var(--gold); font-size: 9px; text-transform: uppercase; }
        .nav-tabs { display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 3px; margin-top: 8px; }
        .nav-btn { background: #1f2937; border: 1px solid var(--gold); color: #fff; padding: 6px 2px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 9px; text-align: center; }
        .nav-btn.active { background: var(--gold); color: #000; }
        .container { padding: 15px; max-width: 1200px; margin: 0 auto; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 20px; }
        .metric-card { background: var(--card-bg); padding: 12px; border-radius: 8px; text-align: center; border: 1px solid var(--border); }
        .metric-card h4 { margin: 0; color: var(--text-muted); font-size: 10px; text-transform: uppercase; }
        .metric-card p { font-size: 16px; font-weight: bold; color: var(--gold); margin: 5px 0 0; }
        .card-box { background: var(--card-bg); padding: 15px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 15px; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; }
        input, select, textarea, button { padding: 8px 10px; border: 1px solid var(--border); background: #0b0f19; color: #fff; border-radius: 5px; box-sizing: border-box; width: 100%; font-family: inherit; font-size: 12px; }
        button { background: var(--gold); color: #000; font-weight: bold; border: none; cursor: pointer; }
        button:hover { opacity: 0.9; }
        .kanban-board { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; align-items: start; }
        .column { background: #111827; border-radius: 8px; padding: 8px; min-height: 350px; border: 1px solid var(--border); }
        .column-header { font-size: 12px; font-weight: bold; margin-bottom: 8px; padding: 4px; display: flex; justify-content: space-between; border-bottom: 2px solid var(--gold); color: var(--gold); }
        .kanban-card { background: #0b0f19; border-radius: 6px; padding: 10px; margin-bottom: 8px; border: 1px solid var(--border); }
        .kanban-card h4 { margin: 0 0 4px 0; color: #fff; font-size: 13px; }
        .kanban-card p { margin: 2px 0; font-size: 10px; color: var(--text-muted); }
        .kanban-card .valor { font-weight: bold; color: var(--whatsapp); font-size: 12px; margin-top: 4px; }
        .tag-quente { background: #dc2626; color: #fff; padding: 2px 5px; border-radius: 3px; font-size: 8px; font-weight: bold; }
        .tag-morno { background: #d97706; color: #fff; padding: 2px 5px; border-radius: 3px; font-size: 8px; font-weight: bold; }
        .tag-frio { background: #2563eb; color: #fff; padding: 2px 5px; border-radius: 3px; font-size: 8px; font-weight: bold; }
        .acoes-card { display: flex; gap: 3px; margin-top: 6px; flex-wrap: wrap; }
        .btn-acao { background: var(--whatsapp); color: white; text-decoration: none; padding: 4px 6px; font-size: 9px; border-radius: 3px; text-align: center; font-weight: bold; flex: 1; display: inline-block; cursor: pointer; border: none; }
        .btn-prop { background: #3b82f6; }
        .btn-chat { background: #8b5cf6; }
        .btn-del { background: #dc3545; }
        .dre-table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 13px; }
        .dre-table th, .dre-table td { padding: 10px; border-bottom: 1px solid var(--border); text-align: left; }
        .dre-table th { color: var(--gold); background: #030712; }
        .dre-total { font-weight: bold; color: var(--whatsapp); font-size: 15px; background: #111827; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th, td { border-bottom: 1px solid var(--border); padding: 7px; text-align: left; }
        th { color: var(--gold); }

        /* Estilo da App de Chat Dedicada */
        .chat-app-grid { display: grid; grid-template-columns: 280px 1fr; gap: 15px; height: 500px; }
        .chat-sidebar { background: #030712; border-radius: 8px; border: 1px solid var(--border); overflow-y: auto; padding: 10px; }
        .chat-item { padding: 10px; border-radius: 6px; margin-bottom: 6px; cursor: pointer; background: #111827; border: 1px solid var(--border); }
        .chat-item:hover, .chat-item.active { background: #1f2937; border-color: var(--gold); }
        .chat-main-area { background: #030712; border-radius: 8px; border: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
        .chat-main-header { padding: 12px; background: #111827; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .chat-messages-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; background: #0b0f19; }
        .msg-bubble { padding: 8px 12px; border-radius: 8px; max-width: 75%; font-size: 12px; line-height: 1.4; }
        .msg-atendente { background: #1f2937; align-self: flex-end; color: #fff; border-right: 3px solid var(--whatsapp); }
        .chat-input-area { padding: 10px; background: #111827; display: flex; gap: 8px; border-top: 1px solid var(--border); }
        @media(max-width: 768px) { .chat-app-grid { grid-template-columns: 1fr; height: auto; } .chat-sidebar { height: 180px; } .chat-main-area { height: 380px; } }
    </style>
</head>
<body>
    <header>
        <div class="logo-box">
            <div class="logo-symbol">♾️</div>
            <div class="logo-title">
                <h1>CONVERIS ENTERPRISE</h1>
                <small>Suite Completa • Central de Atendimento & Chat</small>
            </div>
        </div>
        <div class="nav-tabs">
            <button class="nav-btn active" onclick="mudarAba('kanban', this)">📋 Leads</button>
            <button class="nav-btn" onclick="mudarAba('inicio', this)">🏠 Dashboard</button>
            <button class="nav-btn" onclick="mudarAba('forecasting', this)">📈 Forecast</button>
            <button class="nav-btn" onclick="mudarAba('financeiro', this)">💰 Financeiro</button>
            <button class="nav-btn" onclick="mudarAba('chatApp', this)">💬 Atendimento</button>
            <button class="nav-btn" onclick="mudarAba('suporte', this)">🎫 Pós-Venda</button>
            <button class="nav-btn" onclick="mudarAba('catalogo', this)">📂 Catálogo</button>
            <button class="nav-btn" onclick="mudarAba('treinamento', this)">🎓 Treino</button>
        </div>
    </header>

    <div class="container">
        <!-- ABA 1: KANBAN -->
        <div id="aba-kanban" class="tab-content active">
            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">➕ Cadastrar Conta / Lead B2B & Condição de Pagamento</h3>
                <form id="formCliente" class="form-grid">
                    <input type="text" id="nome" placeholder="Nome do Contato *" required>
                    <input type="text" id="empresa" placeholder="Empresa / Serviço">
                    <input type="text" id="cnpj" placeholder="CNPJ (Opcional)">
                    <input type="text" id="telefone" placeholder="WhatsApp (51999...) *" required>
                    <input type="number" step="0.01" id="valor" placeholder="Valor Total (R$)" required>
                    
                    <select id="tipo_pagamento" onchange="atualizarCamposPagamento()">
                        <option value="À Vista">Pagto: À Vista</option>
                        <option value="A Prazo">Pagto: A Prazo</option>
                    </select>

                    <input type="number" id="parcelas" placeholder="Qtd Parcelas" value="1" min="1">
                    <input type="number" step="0.01" id="valor_pago" placeholder="Valor já pago (R$)" value="0">

                    <select id="vendedor">
                        <option value="Aquiles">Vendedor: Aquiles</option>
                        <option value="Equipe Comercial">Vendedor: Equipe Comercial</option>
                    </select>
                    <select id="temperatura">
                        <option value="Morno">Lead Morno</option>
                        <option value="Quente">Lead Quente 🔥</option>
                        <option value="Frio">Lead Frio ❄️</option>
                    </select>
                    <select id="status">
                        <option value="Novo Lead">Novo Lead</option>
                        <option value="Em Contato">Em Análise</option>
                        <option value="Proposta">Proposta Enviada</option>
                        <option value="Fechado">Contrato Fechado</option>
                        <option value="Perdido">Perdido</option>
                    </select>
                    <textarea id="historico" placeholder="Anotações / Histórico..." rows="2" style="grid-column: 1 / -1;"></textarea>
                    <button type="submit" style="grid-column: 1 / -1;">Salvar Conta no CRM</button>
                </form>
            </div>

            <div class="kanban-board">
                <div class="column" id="col-Novo Lead"><div class="column-header">🔵 Novo Lead <span id="cnt-Novo Lead">(0)</span></div><div class="cards"></div></div>
                <div class="column" id="col-Em Contato"><div class="column-header">🟡 Em Análise <span id="cnt-Em Contato">(0)</span></div><div class="cards"></div></div>
                <div class="column" id="col-Proposta"><div class="column-header">🟠 Proposta Enviada <span id="cnt-Proposta">(0)</span></div><div class="cards"></div></div>
                <div class="column" id="col-Fechado"><div class="column-header">🟢 Contrato Fechado <span id="cnt-Fechado">(0)</span></div><div class="cards"></div></div>
                <div class="column" id="col-Perdido"><div class="column-header">🔴 Perdido <span id="cnt-Perdido">(0)</span></div><div class="cards"></div></div>
            </div>
        </div>

        <!-- ABA 2: DASHBOARD -->
        <div id="aba-inicio" class="tab-content">
            <div class="metrics-grid">
                <div class="metric-card"><h4>Total de Contas</h4><p id="dashTotalLeads">0</p></div>
                <div class="metric-card"><h4>Contratos Fechados</h4><p id="dashFechados" style="color: var(--whatsapp);">0</p></div>
                <div class="metric-card"><h4>Pipeline em Aberto</h4><p id="dashValorAberto">R$ 0,00</p></div>
            </div>
            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">📌 Últimas Contas Cadastradas</h3>
                <table>
                    <thead><tr><th>Contato / Empresa</th><th>Vendedor</th><th>Status</th></tr></thead>
                    <tbody id="tabelaRecentes"></tbody>
                </table>
            </div>
        </div>

        <!-- ABA 3: FORECASTING -->
        <div id="aba-forecasting" class="tab-content">
            <div class="metrics-grid">
                <div class="metric-card"><h4>Faturamento Realizado</h4><p id="fcRealizado" style="color: var(--whatsapp);">R$ 0,00</p></div>
                <div class="metric-card"><h4>Pipeline Potencial</h4><p id="fcPipeline" style="color: var(--gold);">R$ 0,00</p></div>
                <div class="metric-card"><h4>Previsão Total</h4><p id="fcPrevisao" style="color: #3b82f6;">R$ 0,00</p></div>
            </div>
            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">📈 Análise Preditiva de Fechamento</h3>
                <p style="color:var(--text-muted); font-size: 12px;">Projeção baseada nos contratos ativos em andamento.</p>
            </div>
        </div>

        <!-- ABA 4: FINANCEIRO & EXTRATO -->
        <div id="aba-financeiro" class="tab-content">
            <div class="metrics-grid">
                <div class="metric-card"><h4>Já Recebido (Caixa)</h4><p id="finRecebido" style="color: var(--whatsapp);">R$ 0,00</p></div>
                <div class="metric-card"><h4>A Receber (Falta Pagar)</h4><p id="finAReceber" style="color: var(--gold);">R$ 0,00</p></div>
                <div class="metric-card"><h4>Total Inadimplente</h4><p id="finDevendo" style="color: #ef4444;">R$ 0,00</p></div>
            </div>

            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">📋 Extrato Financeiro Individual por Cliente</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Cliente / Empresa</th>
                            <th>Tipo</th>
                            <th>Valor Total</th>
                            <th>Já Pago</th>
                            <th>Falta Pagar</th>
                            <th>Situação</th>
                            <th>Ação</th>
                        </tr>
                    </thead>
                    <tbody id="tabelaExtratoIndividual"></tbody>
                </table>
            </div>

            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">📊 DRE Corporativa Detalhada</h3>
                <table class="dre-table">
                    <tr><td>(+) Receita Total Contratada</td><td id="dreRecBruta" style="text-align: right; color: var(--whatsapp); font-weight: bold;">R$ 0,00</td></tr>
                    <tr><td>(-) Deduções e Impostos (~8%)</td><td id="dreImpostos" style="text-align: right; color: #ef4444;">R$ 0,00</td></tr>
                    <tr style="background: #1f2937;"><td><b>(=) Receita Líquida</b></td><td id="dreRecLiquida" style="text-align: right; font-weight: bold;">R$ 0,00</td></tr>
                    <tr><td>(-) Custos e Despesas Operacionais</td><td id="dreDespesas" style="text-align: right; color: #ef4444;">R$ 0,00</td></tr>
                    <tr class="dre-total"><td>(=) LUCRO LÍQUIDO DO EXERCÍCIO</td><td id="dreLucroFinal" style="text-align: right;">R$ 0,00</td></tr>
                </table>
            </div>

            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">➕ Cadastrar Despesa Operacional</h3>
                <form id="formDespesa" class="form-grid" style="margin-bottom: 12px;">
                    <input type="text" id="descDespesa" placeholder="Descrição" required>
                    <input type="number" step="0.01" id="valDespesa" placeholder="Valor (R$)" required>
                    <button type="submit">Adicionar</button>
                </form>
                <table>
                    <thead><tr><th>Descrição</th><th>Valor</th><th>Ação</th></tr></thead>
                    <tbody id="listaDespesasCorpo"></tbody>
                </table>
            </div>
        </div>

        <!-- ABA 5: APP DE CHAT DEDICADA -->
        <div id="aba-chatApp" class="tab-content">
            <div class="card-box" style="padding: 10px;">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">💬 Central de Atendimento WhatsApp</h3>
                <div class="chat-app-grid">
                    <div class="chat-sidebar" id="listaClientesChatApp">
                        <p style="color:var(--text-muted); font-size:11px; text-align:center;">Carregando clientes...</p>
                    </div>
                    <div class="chat-main-area">
                        <div class="chat-main-header">
                            <div>
                                <h4 id="chatAppNome" style="margin:0; color:var(--gold); font-size:14px;">Selecione um cliente ao lado</h4>
                                <small id="chatAppTel" style="color:var(--text-muted); font-size:10px;"></small>
                            </div>
                            <a id="btnZapApp" href="#" target="_blank" class="btn-acao" style="display:none; padding:5px 10px; font-size:10px;">📱 Abrir no WhatsApp</a>
                        </div>
                        <div class="chat-messages-box" id="chatAppMensagens">
                            <p style="color:var(--text-muted); text-align:center; font-size:12px; margin-top:50px;">Escolha uma conversa para iniciar o atendimento.</p>
                        </div>
                        <div class="chat-input-area">
                            <input type="text" id="inputChatApp" placeholder="Digite sua mensagem..." onkeypress="if(event.key === 'Enter') enviarMsgApp()" disabled>
                            <button id="btnEnviarApp" onclick="enviarMsgApp()" style="background:var(--whatsapp); color:#000; padding:0 15px;" disabled>Enviar</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ABA 6: SUPORTE -->
        <div id="aba-suporte" class="tab-content">
            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">🎫 Abrir Chamado de Pós-Venda</h3>
                <form id="formTicket" class="form-grid">
                    <select id="ticketClienteId" required style="grid-column: 1 / -1;"><option value="">Selecione o Cliente...</option></select>
                    <input type="text" id="ticketAssunto" placeholder="Assunto" required>
                    <select id="ticketPrioridade"><option value="Normal">Normal</option><option value="Urgente">Urgente 🔥</option></select>
                    <textarea id="ticketDescricao" placeholder="Detalhes..." rows="2" style="grid-column: 1 / -1;"></textarea>
                    <button type="submit" style="grid-column: 1 / -1;">Criar Chamado</button>
                </form>
            </div>
            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">📋 Chamados Ativos</h3>
                <table>
                    <thead><tr><th>Cliente</th><th>Assunto</th><th>Prioridade</th><th>Status</th><th>Ação</th></tr></thead>
                    <tbody id="tabelaTickets"></tbody>
                </table>
            </div>
        </div>

        <!-- ABA 7: CATÁLOGO -->
        <div id="aba-catalogo" class="tab-content">
            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">📂 Soluções Converis</h3>
                <ul>
                    <li>⚖️ Lei do Superendividamento</li>
                    <li>🚗 Financiamento de Veículos / Parcelas Atrasadas</li>
                    <li>💳 Renegociação de Cartão de Crédito</li>
                    <li>👴 Empréstimo Consignado INSS</li>
                </ul>
            </div>
        </div>

        <!-- ABA 8: TREINAMENTO -->
        <div id="aba-treinamento" class="tab-content">
            <div class="card-box">
                <h3 style="color:var(--gold); margin-top:0; font-size:15px;">🎓 Treinamento e Script de Vendas</h3>
                <p style="font-size:13px; line-height:1.5;">
                    <b>Script Inicial:</b><br>
                    <i>"Olá [Nome], sou o(a) atendente da CONVERIS Soluções Financeiras! Vi que solicitou suporte para [Serviço]. Vamos analisar o seu caso?"</i>
                </p>
            </div>
        </div>
    </div>

    <script>
        const colunas = ['Novo Lead', 'Em Contato', 'Proposta', 'Fechado', 'Perdido'];
        let clienteChatAppAtivo = null;
        let telefoneChatAppAtivo = '';

        function mudarAba(nomeAba, elemento) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(`aba-${nomeAba}`).classList.add('active');
            if(elemento) elemento.classList.add('active');
            if(nomeAba === 'chatApp') carregarListaChatApp();
        }

        function atualizarCamposPagamento() {
            const tipo = document.getElementById('tipo_pagamento').value;
            const campoParcelas = document.getElementById('parcelas');
            const campoPago = document.getElementById('valor_pago');
            const campoValorTotal = document.getElementById('valor');

            if (tipo === 'À Vista') {
                campoParcelas.value = 1;
                campoParcelas.disabled = true;
                campoPago.value = campoValorTotal.value || 0;
            } else {
                campoParcelas.disabled = false;
                campoParcelas.value = 2;
            }
        }

        document.getElementById('valor').oninput = function() {
            const tipo = document.getElementById('tipo_pagamento').value;
            if (tipo === 'À Vista') {
                document.getElementById('valor_pago').value = this.value;
            }
        };

        // Funções da App de Chat Dedicada
        async function carregarListaChatApp() {
            const res = await fetch('/api/clientes');
            const clientes = await res.json();
            const sidebar = document.getElementById('listaClientesChatApp');
            sidebar.innerHTML = '';

            if(clientes.length === 0) {
                sidebar.innerHTML = '<p style="color:var(--text-muted); font-size:11px; text-align:center;">Nenhum lead cadastrado.</p>';
                return;
            }

            clientes.forEach(c => {
                const ativoClass = clienteChatAppAtivo === c.id ? 'active' : '';
                sidebar.innerHTML += `
                    <div class="chat-item ${ativoClass}" onclick="selecionarChatApp(${c.id}, '${c.nome}', '${c.telefone}')">
                        <div style="font-weight:bold; font-size:12px; color:#fff;">${c.nome}</div>
                        <div style="font-size:10px; color:var(--text-muted);">${c.empresa || 'Geral'} • ${c.status}</div>
                    </div>
                `;
            });
        }

        async function selecionarChatApp(id, nome, telefone) {
            clienteChatAppAtivo = id;
            telefoneChatAppAtivo = telefone;
            document.getElementById('chatAppNome').innerText = nome;
            document.getElementById('chatAppTel').innerText = `WhatsApp: ${telefone}`;
            
            const btnZap = document.getElementById('btnZapApp');
            const numLimpo = telefone.replace(/\D/g,'');
            btnZap.href = `https://api.whatsapp.com/send?phone=${numLimpo}`;
            btnZap.style.display = 'inline-block';

            document.getElementById('inputChatApp').disabled = false;
            document.getElementById('btnEnviarApp').disabled = false;

            carregarListaChatApp();
            carregarMensagensChatApp();
        }

        async function carregarMensagensChatApp() {
            if(!clienteChatAppAtivo) return;
            const res = await fetch(`/api/chat/${clienteChatAppAtivo}`);
            const msgs = await res.json();
            const caixa = document.getElementById('chatAppMensagens');
            caixa.innerHTML = '';
            
            if(msgs.length === 0) {
                caixa.innerHTML = '<p style="color:var(--text-muted); text-align:center; font-size:11px;">Nenhuma mensagem trocada ainda. Envie a primeira!</p>';
                return;
            }

            msgs.forEach(m => {
                caixa.innerHTML += `<div class="msg-bubble msg-atendente"><b>${m.remetente}:</b> ${m.mensagem}<br><small style="font-size:9px; color:#9ca3af;">${m.data_msg}</small></div>`;
            });
            caixa.scrollTop = caixa.scrollHeight;
        }

        async function enviarMsgApp() {
            const input = document.getElementById('inputChatApp');
            const mensagem = input.value.trim();
            if(!mensagem || !clienteChatAppAtivo) return;

            await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cliente_id: clienteChatAppAtivo, remetente: 'Aquiles', mensagem: mensagem })
            });

            input.value = '';
            carregarMensagensChatApp();

            const numLimpo = telefoneChatAppAtivo.replace(/\D/g,'');
            const urlZap = `https://api.whatsapp.com/send?phone=${numLimpo}&text=${encodeURIComponent(mensagem)}`;
            window.open(urlZap, '_blank');
        }

        function abrirChatPorId(id, nome, telefone) {
            mudarAba('chatApp', document.querySelectorAll('.nav-btn')[4]);
            selecionarChatApp(id, nome, telefone);
        }

        function gerarProposta(nome, servico, valor, tipo, parcelas) {
            const texto = `Prezado(a) *${nome}*,\n\nA *CONVERIS Soluções Financeiras* preparou a seguinte proposta comercial para o serviço de *${servico || 'Análise Financeira'}*:\n\n` +
                          `• Valor Total: *R$ ${(valor || 0).toFixed(2)}*\n` +
                          `• Condição: *${tipo} (${parcelas || 1}x)*\n\nPodemos prosseguir com a formalização?`;
            navigator.clipboard.writeText(texto);
            alert(`📋 Proposta copiada para a área de transferência!`);
        }

        async function registrarPagamento(id, nome, faltaPagar) {
            const valorPagoStr = prompt(`Registrar pagamento para ${nome}.\nQuanto deseja dar baixa agora? (Falta: R$ ${faltaPagar.toFixed(2)})`, faltaPagar);
            if(valorPagoStr !== null) {
                const valorAdd = parseFloat(valorPagoStr) || 0;
                if(valorAdd > 0) {
                    await fetch(`/api/clientes/${id}/pagar`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ valor_adicional: valorAdd })
                    });
                    carregarDados();
                }
            }
        }

        async function carregarDados() {
            const res = await fetch('/api/clientes');
            const clientes = await res.json();
            const resDesp = await fetch('/api/despesas');
            const despesas = await resDesp.json();
            const resTick = await fetch('/api/tickets');
            const tickets = await resTick.json();

            document.getElementById('dashTotalLeads').innerText = clientes.length;
            
            let valorAberto = 0, valorFechado = 0, fechadosCount = 0;
            let totalRecebidoCaixa = 0, totalDevendoGeral = 0;
            
            const tabelaRecentes = document.getElementById('tabelaRecentes');
            tabelaRecentes.innerHTML = '';
            const selectCliente = document.getElementById('ticketClienteId');
            selectCliente.innerHTML = '<option value="">Selecione o Cliente...</option>';
            const tabelaExtratoIndividual = document.getElementById('tabelaExtratoIndividual');
            tabelaExtratoIndividual.innerHTML = '';

            clientes.forEach((c, index) => {
                const val = c.valor || 0;
                const pago = c.valor_pago || 0;
                const devendo = Math.max(0, val - pago);

                if (c.status === 'Fechado') {
                    fechadosCount++;
                    valorFechado += val;
                    totalRecebidoCaixa += pago;
                    totalDevendoGeral += devendo;

                    let situacaoBadge = devendo === 0 ? '<span style="color:var(--whatsapp); font-weight:bold;">Quitado ✅</span>' : '<span style="color:#ef4444; font-weight:bold;">Devendo ⚠️</span>';

                    tabelaExtratoIndividual.innerHTML += `
                        <tr>
                            <td><b>${c.nome}</b><br><small>${c.empresa || 'Geral'}</small></td>
                            <td>${c.tipo_pagamento || 'À Vista'} (${c.parcelas || 1}x)</td>
                            <td>R$ ${val.toFixed(2)}</td>
                            <td style="color:var(--whatsapp);">R$ ${pago.toFixed(2)}</td>
                            <td style="color: ${devendo > 0 ? '#ef4444' : 'var(--whatsapp);'}">R$ ${devendo.toFixed(2)}</td>
                            <td>${situacaoBadge}</td>
                            <td><button style="background:var(--whatsapp); color:#000; padding:4px 8px; font-size:10px;" onclick="registrarPagamento(${c.id}, '${c.nome}', ${devendo})">💵 Baixa</button></td>
                        </tr>
                    `;
                } else if (c.status !== 'Perdido') {
                    valorAberto += val;
                }

                selectCliente.innerHTML += `<option value="${c.id}">${c.nome} (${c.empresa || 'Geral'})</option>`;
                if (index < 5) {
                    tabelaRecentes.innerHTML += `<tr><td><b>${c.nome}</b><br><small>${c.empresa || '-'}</small></td><td>${c.vendedor || 'Aquiles'}</td><td><small>${c.status}</small></td></tr>`;
                }
            });

            document.getElementById('dashFechados').innerText = fechadosCount;
            document.getElementById('dashValorAberto').innerText = `R$ ${valorAberto.toFixed(2)}`;

            document.getElementById('fcRealizado').innerText = `R$ ${valorFechado.toFixed(2)}`;
            document.getElementById('fcPipeline').innerText = `R$ ${valorAberto.toFixed(2)}`;
            document.getElementById('fcPrevisao').innerText = `R$ ${(valorFechado + (valorAberto * 0.5)).toFixed(2)}`;

            document.getElementById('finRecebido').innerText = `R$ ${totalRecebidoCaixa.toFixed(2)}`;
            document.getElementById('finAReceber').innerText = `R$ ${totalDevendoGeral.toFixed(2)}`;
            document.getElementById('finDevendo').innerText = `R$ ${totalDevendoGeral.toFixed(2)}`;

            const impostoEstimado = valorFechado * 0.08;
            const recLiquida = valorFechado - impostoEstimado;
            let totalDespesas = 0;
            const listaDespesasCorpo = document.getElementById('listaDespesasCorpo');
            listaDespesasCorpo.innerHTML = '';

            despesas.forEach(d => {
                totalDespesas += d.valor;
                listaDespesasCorpo.innerHTML += `<tr><td>${d.descricao}</td><td>R$ ${d.valor.toFixed(2)}</td><td><button style="background:#dc3545; padding:3px 8px; font-size:10px;" onclick="deletarDespesa(${d.id})">Excluir</button></td></tr>`;
            });

            const lucroLiquido = recLiquida - totalDespesas;
            document.getElementById('dreRecBruta').innerText = `R$ ${valorFechado.toFixed(2)}`;
            document.getElementById('dreImpostos').innerText = `R$ ${impostoEstimado.toFixed(2)}`;
            document.getElementById('dreRecLiquida').innerText = `R$ ${recLiquida.toFixed(2)}`;
            document.getElementById('dreDespesas').innerText = `R$ ${totalDespesas.toFixed(2)}`;
            document.getElementById('dreLucroFinal').innerText = `R$ ${lucroLiquido.toFixed(2)}`;

            const tabelaTickets = document.getElementById('tabelaTickets');
            tabelaTickets.innerHTML = '';
            tickets.forEach(t => {
                tabelaTickets.innerHTML += `<tr><td><b>${t.nome_cliente}</b></td><td>${t.assunto}</td><td>${t.prioridade}</td><td><small style="color:var(--gold);">${t.status_ticket}</small></td><td><button style="background:#dc3545; padding:3px 8px; font-size:10px;" onclick="deletarTicket(${t.id})">Encerrar</button></td></tr>`;
            });

            colunas.forEach(col => { document.querySelector(`#col-${CSS.escape(col)} .cards`).innerHTML = ''; });
            const contadores = { 'Novo Lead': 0, 'Em Contato': 0, 'Proposta': 0, 'Fechado': 0, 'Perdido': 0 };

            clientes.forEach(c => {
                const colTarget = colunas.includes(c.status) ? c.status : 'Novo Lead';
                contadores[colTarget]++;
                let tagTemp = c.temperatura === 'Quente' ? '<span class="tag-quente">QUENTE 🔥</span>' : (c.temperatura === 'Frio' ? '<span class="tag-frio">FRIO ❄️</span>' : '<span class="tag-morno">MORNO</span>');

                const cardHtml = `
                    <div class="kanban-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                            <h4 style="margin:0;">${c.nome}</h4>${tagTemp}
                        </div>
                        <p>🏢 <b>Empresa:</b> ${c.empresa || 'Geral'}</p>
                        <p>💳 <b>Pagto:</b> ${c.tipo_pagamento || 'À Vista'} (${c.parcelas || 1}x)</p>
                        <p>💰 <b>Pago:</b> R$ ${(c.valor_pago || 0).toFixed(2)}</p>
                        <div class="valor">R$ ${(c.valor || 0).toFixed(2)}</div>
                        <select onchange="mudarStatus(${c.id}, this.value)" style="margin-top:4px;">
                            ${colunas.map(st => `<option value="${st}" ${st === c.status ? 'selected' : ''}>Mover: ${st}</option>`).join('')}
                        </select>
                        <div class="acoes-card">
                            <button class="btn-acao btn-chat" onclick="abrirChatPorId(${c.id}, '${c.nome}', '${c.telefone}')">💬 Chat</button>
                            <button class="btn-acao btn-prop" onclick="gerarProposta('${c.nome}', '${c.empresa}', ${c.valor}, '${c.tipo_pagamento}', ${c.parcelas})">📄 Prop.</button>
                            <button class="btn-acao btn-del" onclick="deletarCliente(${c.id})">🗑️</button>
                        </div>
                    </div>
                `;
                document.querySelector(`#col-${CSS.escape(colTarget)} .cards`).innerHTML += cardHtml;
            });

            colunas.forEach(col => { document.getElementById(`cnt-${col}`).innerText = `(${contadores[col]})`; });
        }

        document.getElementById('formCliente').onsubmit = async (e) => {
            e.preventDefault();
            const dados = {
                nome: document.getElementById('nome').value,
                empresa: document.getElementById('empresa').value,
                cnpj: document.getElementById('cnpj').value,
                telefone: document.getElementById('telefone').value,
                valor: parseFloat(document.getElementById('valor').value) || 0,
                tipo_pagamento: document.getElementById('tipo_pagamento').value,
                parcelas: parseInt(document.getElementById('parcelas').value) || 1,
                valor_pago: parseFloat(document.getElementById('valor_pago').value) || 0,
                vendedor: document.getElementById('vendedor').value,
                temperatura: document.getElementById('temperatura').value,
                status: document.getElementById('status').value,
                historico: document.getElementById('historico').value
            };
            await fetch('/api/clientes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
            document.getElementById('formCliente').reset();
            atualizarCamposPagamento();
            carregarDados();
        };

        document.getElementById('formDespesa').onsubmit = async (e) => {
            e.preventDefault();
            const dados = { descricao: document.getElementById('descDespesa').value, valor: parseFloat(document.getElementById('valDespesa').value) || 0 };
            await fetch('/api/despesas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
            document.getElementById('formDespesa').reset();
            carregarDados();
        };

        document.getElementById('formTicket').onsubmit = async (e) => {
            e.preventDefault();
            const dados = { cliente_id: document.getElementById('ticketClienteId').value, assunto: document.getElementById('ticketAssunto').value, prioridade: document.getElementById('ticketPrioridade').value, descricao: document.getElementById('ticketDescricao').value };
            await fetch('/api/tickets', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dados) });
            document.getElementById('formTicket').reset();
            carregarDados();
        };

        async function mudarStatus(id, novoStatus) {
            await fetch(`/api/clientes/${id}/status`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: novoStatus }) });
            carregarDados();
        }

        async function deletarCliente(id) { if(confirm('Excluir?')) { await fetch(`/api/clientes/${id}`, { method: 'DELETE' }); carregarDados(); } }
        async function deletarDespesa(id) { await fetch(`/api/despesas/${id}`, { method: 'DELETE' }); carregarDados(); }
        async function deletarTicket(id) { await fetch(`/api/tickets/${id}`, { method: 'DELETE' }); carregarDados(); }

        setInterval(carregarDados, 5000);
        carregarDados();
    </script>
</body>
</html>
'''

@app.route('/crm')
def pagina_crm():
    return render_template_string(HTML_CRM)

@app.route('/')
def pagina_catalogo_simples():
    return render_template_string('<body style="background:#0b0f19; color:#fff; font-family:sans-serif; text-align:center; padding-top:50px;"><h1>CONVERIS ENTERPRISE</h1><br><a href="/crm" style="background:#d4af37; color:#000; padding:12px 20px; text-decoration:none; font-weight:bold; border-radius:5px;">Abrir Painel</a></body>')

@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    with get_db() as conn:
        return jsonify([dict(row) for row in conn.execute("SELECT * FROM clientes ORDER BY id DESC").fetchall()])

@app.route('/api/clientes', methods=['POST'])
def adicionar_cliente():
    d = request.get_json()
    with get_db() as conn:
        conn.execute("INSERT INTO clientes (nome, empresa, cnpj, telefone, status, vendedor, temperatura, valor, tipo_pagamento, parcelas, valor_pago, historico) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (d.get('nome'), d.get('empresa'), d.get('cnpj'), d.get('telefone'), d.get('status'), d.get('vendedor'), d.get('temperatura'), d.get('valor'), d.get('tipo_pagamento'), d.get('parcelas'), d.get('valor_pago'), d.get('historico')))
        conn.commit()
    return jsonify({"status": "sucesso"}), 201

@app.route('/api/clientes/<int:id>/status', methods=['PUT'])
def atualizar_status(id):
    with get_db() as conn:
        conn.execute("UPDATE clientes SET status = ? WHERE id = ?", (request.get_json().get('status'), id))
        conn.commit()
    return jsonify({"status": "atualizado"})

@app.route('/api/clientes/<int:id>/pagar', methods=['PUT'])
def registrar_pagamento(id):
    d = request.get_json()
    val_add = d.get('valor_adicional', 0)
    with get_db() as conn:
        conn.execute("UPDATE clientes SET valor_pago = valor_pago + ? WHERE id = ?", (val_add, id))
        conn.commit()
    return jsonify({"status": "pago_atualizado"})

@app.route('/api/chat/<int:cliente_id>', methods=['GET'])
def listar_mensagens_chat(cliente_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_mensagens WHERE cliente_id = ? ORDER BY id ASC", (cliente_id,))
        return jsonify([dict(row) for row in cursor.fetchall()])

@app.route('/api/chat', methods=['POST'])
def enviar_mensagem_chat():
    d = request.get_json()
    with get_db() as conn:
        conn.execute("INSERT INTO chat_mensagens (cliente_id, remetente, mensagem) VALUES (?, ?, ?)",
                     (d.get('cliente_id'), d.get('remetente', 'Aquiles'), d.get('mensagem')))
        conn.commit()
    return jsonify({"status": "enviado"}), 201

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def deletar_cliente(id):
    with get_db() as conn:
        conn.execute("DELETE FROM clientes WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"status": "removido"})

@app.route('/api/despesas', methods=['GET', 'POST'])
def gerenciar_despesas():
    with get_db() as conn:
        if request.method == 'POST':
            d = request.get_json()
            conn.execute("INSERT INTO despesas (descricao, valor) VALUES (?, ?)", (d.get('descricao'), d.get('valor')))
            conn.commit()
            return jsonify({"status": "sucesso"}), 201
        return jsonify([dict(row) for row in conn.execute("SELECT * FROM despesas ORDER BY id DESC").fetchall()])

@app.route('/api/despesas/<int:id>', methods=['DELETE'])
def deletar_despesa(id):
    with get_db() as conn:
        conn.execute("DELETE FROM despesas WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"status": "removido"})

@app.route('/api/tickets', methods=['GET', 'POST'])
def gerenciar_tickets():
    with get_db() as conn:
        if request.method == 'POST':
            d = request.get_json()
            conn.execute("INSERT INTO tickets (cliente_id, assunto, prioridade, descricao) VALUES (?, ?, ?, ?)", 
                         (d.get('cliente_id'), d.get('assunto'), d.get('prioridade'), d.get('descricao')))
            conn.commit()
            return jsonify({"status": "sucesso"}), 201
        return jsonify([dict(row) for row in conn.execute("SELECT t.*, c.nome as nome_cliente FROM tickets t JOIN clientes c ON t.cliente_id = c.id ORDER BY t.id DESC").fetchall()])

@app.route('/api/tickets/<int:id>', methods=['DELETE'])
def deletar_ticket(id):
    with get_db() as conn:
        conn.execute("DELETE FROM tickets WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"status": "removido"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
