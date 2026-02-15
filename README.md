# 💰 Gestor de Despesas Pro

Sistema completo para controle financeiro pessoal ou empresarial, desenvolvido em Python.

## 🚀 Funcionalidades
- **Cadastro de Despesas:** Registro com data, categoria, valor e histórico.
- **Dashboard Dinâmico:** Visualização do saldo total e gastos do mês.
- **Relatórios Contábeis:** Geração de PDF filtrado por período com soma total automática.
- **Interface Moderna:** Construído com `CustomTkinter` para uma aparência atual.

## 🛠️ Tecnologias Utilizadas
- Python 3
- Pandas (Tratamento de dados)
- FPDF (Geração de relatórios)
- CustomTkinter (Interface gráfica)

## 📦 Como gerar o Executável (.exe)
Para usar o programa fora do ambiente de desenvolvimento:
```bash
python -m PyInstaller --onefile --noconsole --clean --collect-all customtkinter main.py
