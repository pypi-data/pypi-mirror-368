class Bar:
    """
    A basic class for printing rows of same emojis

    Parameters:

    emoji(str) : The emoji to be repeated
    """

    def __init__(self, emoji: str):
        self.emoji = emoji

    def return_bar(self, length: int) -> str:
        """
        Prints out a row of emojis

        Parameters:

        length(int) : The number of times the emoji shoudl be repeated
        """
        output = ""
        for i in range(0, length):
            output += self.emoji
        return output


# Basic tests
if __name__ == "__main__":
    testBar = Bar("🏓")
    print(testBar.return_bar(10))
