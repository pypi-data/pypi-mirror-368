# This contains the main code

# These are just for the nice terminal colour
GREEN = "\033[32m"
RED = "\033[31m"

RESET = "\033[0m"  # Resets to default terminal color

import warnings
import time


class LoadingBar:
    def __init__(
        self, on_emoji: str, off_emoji: str, capacity: int, isPercentage: bool = False
    ):
        self.on_emoji = on_emoji
        self.off_emoji = off_emoji
        self.capacity = capacity
        self.isPercentage = isPercentage

    def print_bar(
        self,
        value: int,
        prefix: str,
        suffix: str = "",
        display_status=True,
        end=False,
    ):
        output = ""
        status = ""
        if value > self.capacity:
            warnings.warn("value must be smaller than total capacity")
        else:
            for i in range(0, self.capacity):
                if i < value:
                    output = output + self.on_emoji
                else:
                    output = output + self.off_emoji

        if self.isPercentage:
            status = round(value / self.capacity * 100)
            if not end:
                print(
                    f"{prefix} {GREEN} {output} {suffix} {GREEN if value == self.capacity else RED} {status if display_status else ''}% {RESET}",
                    end="\r",
                )
            else:
                print(
                    f"{prefix} {GREEN} {output} {suffix} {GREEN if value == self.capacity else RED} {status if display_status else ''}% {RESET}",
                    end="\n",
                )
        else:
            status = str(value) + "/" + str(self.capacity)
            if not end:
                print(
                    f"{prefix} {GREEN} {output} {suffix} {GREEN if value == self.capacity else RED} {status if display_status else ''} {RESET}",
                    end="\r",
                )
            else:
                print(
                    f"{prefix} {GREEN} {output} {suffix} {GREEN if value == self.capacity else RED} {status if display_status else ''} {RESET}",
                    end="\n",
                )


if __name__ == "__main__":
    testBar = LoadingBar("█", "▒", 10)
    for i in range(0, testBar.capacity + 1):
        testBar.print_bar(i, "Loading:")
        time.sleep(0.5)
