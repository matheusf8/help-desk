# Etapa 5 — Documentação

**Objetivo:** deixar o projeto explicado no mesmo padrão do api_cadastro: quem abre o repositório entende o que é, como rodar, por que foi feito assim e o que ainda falta.
**Resultado:** `docs/` completa e README reescrito.

## O que foi criado

| Arquivo | Para quê |
|---|---|
| `docs/arquitetura.md` | camadas, fluxo de uma limpeza (diagrama) e estrutura de pastas |
| `docs/decisoes.md` | 18 decisões com motivo e alternativa |
| `docs/seguranca.md` | regras e onde cada uma é garantida no código, achados da revisão e riscos que restam |
| `docs/como-rodar.md` | instalação, uso das opções, testes e problemas comuns |
| `docs/entrevista.md` | pitch de 1 minuto, 17 perguntas com resposta curta e o que não falar |
| `docs/etapas/` | um arquivo por etapa (0 a 5), com o passo a passo |
| `README.md` | visão geral, tabela de stack, fluxo, estrutura, mapa da documentação e limites conhecidos |

## Como foi feito
1. Reuni o raciocínio que estava espalhado em comentários do código e no README antigo e separei por assunto (como/por quê/risco).
2. Cada afirmação de segurança aponta para o arquivo que a garante, para dar para conferir: se a frase não tem código por trás, ela não entra.
3. Conferi os números citados (54 testes, 25 em `limpeza`, 12 em `menu`) com `pytest --collect-only`.
4. Os "riscos que restam" saíram de uma releitura do código, incluindo o que **não** foi testado (registro do Windows, itens grandes demais para a Lixeira).

## Verificação
| Checagem | Resultado |
|---|---|
| `pytest` | 54 passaram |
| Links do README e dos docs | conferidos um a um |
