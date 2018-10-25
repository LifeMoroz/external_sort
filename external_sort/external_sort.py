import gc
import os
import shutil
import sys
from typing import Tuple


class BlockSorter:
    BLOCK_DIRNAME = 'block'
    BLOCK_FILENAME_TEMPLATE = BLOCK_DIRNAME + '/block_{}.txt'  # py3.5

    def __init__(self, part_size: int):
        """
        :param part_size: размер блока
        """
        self.part_size = part_size
        self.blocks_number = 0

    @classmethod
    def _sort(cls, array: list) -> list:
        """
        Простейшая сортировка пузырьком, как "сортировка на месте"
        :param array: массив для сортировки
        :return: array
        """
        i = 1
        changed = True
        while i < len(array) and changed:
            changed = False
            for j in range(len(array) - i):
                if array[j] > array[j + 1]:
                    array[j], array[j + 1] = array[j + 1], array[j]
                    changed = True
            i += 1
        return array

    @classmethod
    def _merge_sort(cls, arr1: list, arr2: list) -> Tuple[bool, list]:
        """
        Максимальный объём памяти, если gc не проходит:
        120 + (2 * (len(arr2) + len(arr1)) * max_string_size)
        :param arr1: первый блок для сортировки
        :param arr2: второй блок для сортировки
        :return: отсортированный массив
        """
        if not arr1:
            return False, arr2
        if not arr2:
            return False, arr1

        sorted_arr = []
        changed = False
        while arr1:
            if not arr2 or arr1[0] < arr2[0]:
                sorted_arr.append(arr1.pop(0))
            else:
                sorted_arr.append(arr2.pop(0))
                changed = True
        sorted_arr.extend(arr2)
        arr2.clear()
        gc.collect()
        return changed, sorted_arr

    def fill_block(self, block_number: int, data: str) -> None:
        with open(self.BLOCK_FILENAME_TEMPLATE.format(block_number), 'w+') as file:
            file.write(data)

    def read_block(self, block_number: int) -> list:
        with open(self.BLOCK_FILENAME_TEMPLATE.format(block_number), 'r') as file:
            return file.readlines()

    def split(self, file)-> int:
        """
        :param file: файловый дескриптор и дробит его на блоки, каждый блок внутри сортируется.
        :return: количество блоков
        """
        try:
            os.makedirs(self.BLOCK_DIRNAME)
        except OSError:
            print('Возможно папка уже создана', file=sys.stderr)
            pass
        self.blocks_number = 0
        lines = []
        for line in file:
            lines.append(line)
            if len(lines) != self.part_size:
                continue
            print('Split step', self.blocks_number, 'of')
            self._sort(lines)  # In-place sort
            self.fill_block(self.blocks_number, ''.join(lines))
            self.blocks_number += 1
            lines.clear()
        self._sort(lines)  # In-place sort
        self.fill_block(self.blocks_number, ''.join(lines))
        self.blocks_number += 1
        return self.blocks_number

    def sort_blocks(self, block_number_1: int, block_number_2: int):
        """
        Потребляет 4 * O(self.part_size)
        :param block_number_1: номер первого блока
        :param block_number_2: номер второго блока
        :return:
        """
        if block_number_1 > block_number_2:  # меньший
            block_number_1, block_number_2 = block_number_2, block_number_1

        block_1 = self.read_block(block_number_1)
        block_2 = self.read_block(block_number_2)
        changed, sorted_blocks = self._merge_sort(block_1, block_2)

        self.fill_block(block_number_1, ''.join(sorted_blocks[:self.part_size]))
        self.fill_block(block_number_2, ''.join(sorted_blocks[self.part_size:]))
        return changed

    def write_to_file(self, fd):
        for block_number in range(self.blocks_number):
            with open(self.BLOCK_FILENAME_TEMPLATE.format(block_number), 'r') as file:
                for line in file:
                    fd.write(line)

    def clean(self):
        shutil.rmtree(self.BLOCK_DIRNAME)

    def sort(self, fd) -> None:
        self.split(fd)

        if self.blocks_number == 0:  # Пустой файл
            return

        i = 1
        while i < self.blocks_number:
            changed = False
            for j in range(self.blocks_number - i):
                if self.sort_blocks(j, j+1):
                    changed = True
            if not changed:
                return
            i += 1
