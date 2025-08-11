# Bir listenin elemanlarını kolonlar halinde sıralayan fonksiyon:

from sys import stderr

def listele(li:list, kolon:int, ljustmz:int=30):
    """ listele(li:list, kolon:int, ljustmz:int=30)
    """
    try:
        iter(li)
    except:
        print("Listelenemeyen eleman girildi.", file= stderr)
        return
    if not isinstance(kolon, int) or not isinstance(ljustmz, int) or 1 >= kolon > len(li) or ljustmz < 0:
        print("Hatalı parametreler girildi.", file= stderr)
        return

    for i in range(0, len(li)-kolon+1, kolon):
        for j in range(kolon):
            print(str(li[i + j]).ljust(ljustmz), end="")
        print()

    if len(li)%kolon:
        for i in range(len(li)%kolon, 0, -1):
            print(str(li[-i]).ljust(ljustmz), end="")
    print()
