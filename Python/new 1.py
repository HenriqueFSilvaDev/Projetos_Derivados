import requests

# Troque pelo link do seu servidor ngrok
URL_BASE = "https://128d4be3c74f.ngrok-free.app"

while True:
    print("\n=== Cliente de Mensagens ===")
    print("1 - Enviar mensagem")
    print("2 - Listar mensagens")
    print("3 - Sair")

    opcao = input("Escolha: ")

    if opcao == "1":
        msg = input("Digite a mensagem: ")
        resposta = requests.post(f"{URL_BASE}/enviar", json={"mensagem": msg})
        print("Resposta:", resposta.json())

    elif opcao == "2":
        resposta = requests.get(f"{URL_BASE}/listar")
        print("Mensagens:", resposta.json())

    elif opcao == "3":
        print("Encerrando cliente.")
        break

    else:
        print("Opção inválida.")
