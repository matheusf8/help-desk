# Etapa 0 — Estado inicial (v1)

**Objetivo:** registrar como o projeto estava antes da reestruturação, para a próxima pessoa (ou você, na entrevista) saber de onde partiu.
**Resultado:** diagnóstico com o que já era bom e o que faltava.

## O que a v1 já tinha
- Programa de terminal para Windows com menu numerado (diagnóstico e limpeza).
- Código separado em camadas: `main.py` (tela), `faxineira/diagnostico.py` (só lê), `faxineira/limpeza.py` (mexe em arquivo) e `faxineira/utils.py` (funções puras).
- Regra de segurança nº 1: nada é apagado direto, tudo vai para a Lixeira (`send2trash`), com confirmação.
- 10 testes de funções puras (`formatar_bytes`, `calcular_percentual`, `tamanho_pasta`, `maiores_pastas`).

## O que faltava
| Problema | Por que importa |
|---|---|
| `limpeza.py` sem nenhum teste | É justamente o arquivo que apaga coisas. |
| Regra "nunca mexe em Windows, drivers, antivírus..." só existia no texto da tela | O código não impedia nada: era uma promessa, não uma garantia. |
| `main.py` com 263 linhas misturando textos, telas e loop | Difícil de ler e de testar. |
| `rodar_limpeza_chrome` não tratava lista vazia nem as falhas | A de Temp tratava; ficou inconsistente. |
| Sem `docs/`, sem `pytest.ini`, `.gitignore` mínimo, 1 commit só | Quem abre o repositório não vê o raciocínio por trás. |

## Próximas etapas
Veja a tabela no [README](../../README.md#documentação). A ordem é: base do projeto → camadas → trava de itens protegidos → testes → documentação.
