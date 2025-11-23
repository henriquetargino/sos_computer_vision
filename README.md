# ✋🚨 Signal for Help Detector (Computer Vision)

> Um sistema de segurança baseado em Visão Computacional capaz de identificar o "Sinal de Socorro" (Signal for Help) universal em tempo real e disparar alertas via API.

## 🎯 Sobre o Projeto

Este projeto foi desenvolvido para aplicar conceitos de **Ciência de Dados** em um problema do mundo real: segurança pessoal.

Diferente de abordagens tradicionais que exigem o treinamento de modelos pesados de Deep Learning, este sistema utiliza **Geometria Euclidiana** e **Álgebra Linear** para analisar a biomecânica da mão em tempo real usando apenas CPU. O sistema é capaz de diferenciar movimentos aleatórios de um pedido de socorro intencional através de uma **Máquina de Estados Finita (FSM)**.

-----

## 🛠️ Funcionalidades Técnicas

  * **Rastreamento de Mão (Hand Tracking):** Utiliza MediaPipe para extrair 21 landmarks da mão em tempo real.
  * **Lógica Geométrica:** Calcula distâncias vetoriais entre o dedão e a base do mindinho para validar a posição da mão sem depender de pixels fixos (independente de profundidade).
  * **Máquina de Estados Temporal:** O alerta não é disparado por uma foto estática. O sistema valida a **sequência** do movimento (Mão Armada -\> Janela de 2s -\> Punho Fechado).
  * **Processamento Assíncrono (Threading):** O envio da requisição HTTP (Webhook) roda em uma thread separada para evitar o *Blocking I/O*, garantindo que o processamento de vídeo se mantenha fluido a 30 FPS.
  * **Feedback Visual (UI):** Interface reativa com Bounding Boxes dinâmicos, feedback de estado (Verde/Laranja/Vermelho) e flash de tela para confirmação de envio.

-----

## 🧠 Como Funciona (A Lógica)

O algoritmo segue um pipeline de decisão rigoroso para evitar falsos positivos:

1.  **Input:** Captura de vídeo via OpenCV (conversão BGR -\> RGB).
2.  **Vetorização:** Extração das coordenadas `(x, y)` das articulações.
3.  **Estágio 1 (Armar):**
      * O sistema verifica se 4 dedos estão levantados.
      * Calcula a **Distância Euclidiana** (`math.hypot`) entre a ponta do dedão e a base do mindinho. Se a distância for curta (dedão na palma), o sistema entra em estado de **ALERTA (Laranja)**.
4.  **Estágio 2 (Disparar):**
      * Uma janela temporal de 2 segundos é aberta.
      * Se o usuário fechar o punho (todos os dedos baixados) dentro desse tempo, a intenção é confirmada.
5.  **Output:**
      * O sistema dispara um POST Request para um Webhook (n8n no meu caso).
      * A UI pisca em vermelho para confirmar o envio.

-----

## 💻 Tecnologias Utilizadas

  * **Python 3.10** (Ambiente Virtual Conda para compatibilidade com MediaPipe)
  * **OpenCV (`cv2`)**: Manipulação de imagem e desenho de UI.
  * **MediaPipe**: Extração de landmarks.
  * **NumPy & Math**: Cálculos vetoriais e geometria.
  * **Requests**: Integração com API.
  * **Threading**: Gerenciamento de concorrência.

-----

## 🚀 Como Rodar

### Pré-requisitos

Certifique-se de ter o Python instalado (Recomendado Python 3.10).

1.  **Clone o repositório:**

<!-- end list -->

```bash
git clone https://github.com/henriquetargino/sos_computer_vision.git
cd sos_computer_vision
```

2.  **Instale as dependências:**

<!-- end list -->

```bash
pip install opencv-python mediapipe numpy requests
```

3.  **Configure o Webhook (Opcional):**
    No arquivo `main.py`, edite a função `webhook_socorro` e adicione sua URL:

<!-- end list -->

```python
url = "link_webhook_aqui"
```

4.  **Execute:**

<!-- end list -->

```bash
python main.py
```

-----

## 📈 Aprendizados e Desafios

Durante o desenvolvimento, alguns desafios de engenharia foram superados:

  * **Canais de Cor:** O tratamento de matrizes BGR do OpenCV vs RGB dos modelos de IA.
  * **Concorrência:** A implementação de Threading foi crucial. Sem ela, o vídeo "congelava" enquanto o Python aguardava a resposta do servidor HTTP.
  * **UX de Segurança:** A criação de feedbacks visuais (Caixa de Foco e Flash) para dar certeza ao usuário de que o sistema entendeu o comando.

-----

## 📞 Contato

**Henrique Targino** - Cientista de Dados
[LinkedIn](https://www.linkedin.com/in/henriquetargino) | [Portfólio](https://henriquetargino.github.io/Portfolio)

-----

