class Bar:
    def __init__(self, emoji: str):
        self.emoji = emoji

    def return_bar(self, length: int):
        output = ""
        for i in range(0, length):
            output += self.emoji
        return output


# Basic tests
if __name__ == "__main__":
    testBar = Bar("🏓")
    print(testBar.return_bar(10))
