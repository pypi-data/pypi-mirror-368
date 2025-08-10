def razonamiento_basico(palabra):
    """
    Devuelve una respuesta razonada muy básica sobre una palabra conocida.
    """
    if palabra in ["hola", "adiós"]:
        return f"La palabra '{palabra}' se usa en interacciones humanas cotidianas."
    elif palabra in ["python", "bot"]:
        return f"La palabra '{palabra}' se relaciona con tecnología y programación."
    else:
        return f"No tengo un razonamiento especial para '{palabra}', pero puedo aprender."
