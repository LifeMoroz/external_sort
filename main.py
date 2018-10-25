import sys

import psutil

from big_file_generator import CachedRowsGenerator
from external_sort.external_sort import BlockSorter

FILENAME = 'big_file.txt'
LINES_IN_FILE = 100000
MAX_STRING_SIZE = 100


def get_max_part_size(available, max_string_size: int):
    """
    Не строгий подсчёт памяти, рассчёт самого худшего случая и небольшой запас на "неучтённые расходы"
    """
    size = available - 120  # 3 указателя на массив для merge_sort
    size = size / 4  # Худший случай, если за merge_sort gc ни разу не зайдёт
    size = size - 25 * size / max_string_size  # Если бы мы создавали строки на всю доступную память, то это - указатели
    size = size / max_string_size  # Максимальное количество строк
    return int(size) // 4  # Что-то упустил, но результат ровно в 4 раза больше


if __name__ == '__main__':  # TODO: вынести в класс и тоже покрыть тестами
    mem = psutil.virtual_memory()
    available_mem = (min(mem.available, 1048576))  # Искусственно ограничим до 10 Mb
    max_part_size = get_max_part_size(available_mem, MAX_STRING_SIZE)
    if max_part_size <= 20:  # 20 - минимальный буфер
        print("Can't work without memory", file=sys.stderr)
        # TODO: или может, если делать merge не в памяти, но не за 4 часа =)
        sys.exit(-1)

    # generator = CachedRowsGenerator(LINES_IN_FILE, MAX_STRING_SIZE)  # ~ 473 Mb generated
    # if not generator.generate(FILENAME):
    #     print("Failed to generate file", file=sys.stderr)
    #     sys.exit(-1)

    block_1 = []
    block_2 = []
    with open(FILENAME, 'r') as file:
        BlockSorter(max_part_size).sort(file)


# TODO: map reduce
# TODO: Tests for external sort
