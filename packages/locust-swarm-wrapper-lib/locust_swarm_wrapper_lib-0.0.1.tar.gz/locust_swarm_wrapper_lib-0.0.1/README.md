# Locust swarm wrapper lib

## What is it?:

Python library for load testing in browser. Library provide different strategies for load testing.
Simple wrapper lib for another lib, with a little bit of StarCraft 2 in it.

## Target Auditory of the lib:

1. Author of the lib (Cupcake_wrld)
2. Some strangers... (especially on PyPI)
3. Maybe moderators on PyPI site (if they exist)

## What useful opportunities in use this lib?

1. None (I am serious now)

## Locust swarm lib requirements:

1. Python with version 3.12 or above
2. Some storage space on your personal computer

## Locust swarm lib components:

1. App - abstraction class for swarm
2. Swarm class - abstraction class for locusts
3. Locust - main unit in library to "attack" website (Also name of the inner library)
4. Strategies directory with different strategies classes for load testing.
5. Tests - directory with app tests

## Example of using library:

    import <something>    

    page = 'https://yandex.ru'
    """
    Attack this page
    """
    
    if __name__ == "__main__":
        app = LocustSwarm.App(StrategyEnum.PEAK, True, False)
        app.set_swarm_attack_to_page(
            page_to_destroy=page,
            logger=app.get_logger()
        )

    app.get_swarm().proceed_locusts(
        app_runner=app.get_runner(),
        locust_spawn_rate=5,
    )

## Contacts:

### Library author:

1. [Author GitHub account](https://github.com/bob-jacka)
2. [Author contact email](mailto:ccaatt63@gmail.com)