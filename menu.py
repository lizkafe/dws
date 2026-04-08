from embed_extract import *
from ber_ncc import *
def menu():
    action = str(input("Выберите, что хотите сделать:\n 1 - Встроить ЦВЗ\n 2 - Извлечь ЦВЗ\n 3 - Рассчитать BER и NCC\n Ваш выбор: "))
    if action == '1':
        embed()
    if action == '2':
        extract()
    if action == '3':
        calculate_ber_ncc()
        

               

menu()