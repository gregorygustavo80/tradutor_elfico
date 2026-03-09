from translator import SindarinTranslator

def main():
    translator = SindarinTranslator()

    while True:
        print("\n=== Tradutor Português ↔ Sindarin ===")
        print("1 - Português para Sindarin")
        print("2 - Sindarin para Português")
        print("0 - Sair")

        option = input("Escolha: ").strip()

        if option == "0":
            print("Encerrado.")
            break

        text = input("Digite a frase: ")

        if option == "1":
            print("Resultado:", translator.translate_pt_to_sd(text))
        elif option == "2":
            print("Resultado:", translator.translate_sd_to_pt(text))
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()