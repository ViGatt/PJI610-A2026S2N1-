# Controle de Estoque — Alimentação Escolar

Projeto Integrador VI (PJI610) — Engenharia de Computação, UNIVESP
Turma DRP07-A2026S2-T001

## Sobre o projeto

Protótipo de uma plataforma de hardware e software para o controle automatizado
do estoque de gêneros secos e congelados da alimentação escolar, desenvolvido
para a **E.E. Professor Anísio Carneiro** (Tupã/SP).

O projeto **não possui finalidade comercial**. Trata-se de um trabalho
acadêmico do Projeto Integrador da UNIVESP, com aplicação restrita ao cenário
pedagógico da escola parceira.

O problema identificado: o controle de itens de gênero seco e congelado da
merenda escolar é feito de forma manual, por anotações em papel, o que gera
risco de inconsistências entre o que é efetivamente consumido e o que é
formalmente registrado no sistema de abastecimento da escola.

## Arquitetura da solução

O protótipo é composto por três camadas:

1. **Captura de dados (hardware simulado)** — um microcontrolador ESP32
   conectado a um display OLED, simulado no ambiente Wokwi. A leitura de
   produtos (que em uma implementação física seria feita por um leitor de
   código de barras) é representada por botões, preservando a lógica real
   de funcionamento: a cada acionamento, o dispositivo envia a informação
   ao backend via HTTP e exibe a confirmação no display.
2. **Processamento (backend)** — aplicação em Python com FastAPI,
   responsável por receber as leituras, validar os dados e atualizar o
   saldo de estoque em um banco de dados PostgreSQL persistente, hospedada
   em nuvem (Render).
3. **Visualização (frontend)** — painel web que exibe o estoque atual e o
   histórico das últimas baixas registradas, hospedado no mesmo serviço do
   backend.

A simulação de hardware foi adotada para eliminar custos de aquisição de
componentes e a necessidade de deslocamento físico entre os polos do grupo
(Marília, Paraguaçu Paulista, Ipaussu e Tupã) e a escola parceira, mantendo
o backend e o frontend — núcleo funcional da solução — inteiramente reais e
acessíveis publicamente.

## Links do projeto

| Recurso | Link |
|---|---|
| Simulação do circuito (Wokwi) | https://wokwi.com/projects/476545614434059265 |
| Código-fonte (GitHub) | https://github.com/ViGatt/PJI610-A2026S2N1- |
| Painel web / dashboard (Render) | https://pji610-a2026s2n1.onrender.com/ |

> **Observação:** o backend está hospedado no plano gratuito do Render, que
> "adormece" após ~15 minutos de inatividade. O primeiro acesso após esse
> período pode levar de 30 a 50 segundos para responder enquanto o serviço
> é reativado.

## Estrutura do repositório

```
backend_estoque/
├── main.py              # API FastAPI (endpoints de movimentação e estoque)
├── requirements.txt      # dependências Python
└── static/
    └── index.html         # painel web (dashboard)

wokwi_esp32/
├── sketch.ino            # firmware do ESP32
├── diagram.json          # circuito simulado (Wokwi)
└── libraries.txt         # bibliotecas Arduino utilizadas
```

## Tecnologias utilizadas

- **ESP32** (simulado no Wokwi) + display OLED (SSD1306)
- **Python 3 / FastAPI** — backend REST
- **PostgreSQL** — persistência dos dados (banco gratuito do Render)
- **HTML / CSS / JavaScript** — painel web
- **Render** — hospedagem do backend e do painel

## Como funciona (fluxo de uma baixa de estoque)

1. O dispositivo simulado no Wokwi identifica a retirada de um produto
   (botão pressionado) e envia uma requisição `POST /movimentacoes` ao
   backend, informando o código de barras do item.
2. O backend valida o produto, decrementa o saldo em 1 unidade e registra
   a movimentação (produto + data/hora) no banco de dados.
3. O painel web consulta os endpoints `GET /estoque` e
   `GET /movimentacoes/recentes` a cada poucos segundos, exibindo o saldo
   atualizado e o histórico de baixas em tempo real.

## Metodologia

O desenvolvimento seguiu as três etapas orientadas pela UNIVESP para o
Projeto Integrador:

- **Ouvir/Interpretar** — levantamento junto à direção da escola parceira,
  confirmando o controle manual como fator limitante da gestão de estoque.
- **Criar/Prototipar** — definição da arquitetura e desenvolvimento do
  protótipo integrado (hardware simulado + backend + painel web).
- **Implementar/Testar** — validação remota do protótipo por uma
  integrante do grupo que atua na escola parceira, com devolutiva
  incorporada aos ajustes da solução.

## Grupo

- Anderson Aparecido Alves
- Andre Marcatti
- Fernanda Alves Yonekubo
- Marcio Silvio dos Santos
- Melissa Conceição Rodrigues
- Raquel Estanis
- Renata Estanis
- Vinicius Gatti Rodrigues

Orientadora: Fabiana Andrade Barroso

---

*Universidade Virtual do Estado de São Paulo (UNIVESP) — 2026*
