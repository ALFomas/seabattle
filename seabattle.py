# ИТОГОВОЕ ЗАДАНИЕ 2.5.1 (HW-02)


from random import randint
from time import sleep


class BoardException(Exception):
    """ Class Exception"""
    pass


class BoardOutException(BoardException):
    """ shot off the board"""

    def __str__(self) -> str:
        return "Координаты за пределами игровой доски!"


class BoardUsedException(BoardException):
    """ re-shot exceptions"""

    def __str__(self) -> str:
        return "В эту точку уже стреляли!"


class BoardWrongShipException(BoardException):
    """ exception caused by incorrect ship position"""
    pass


class Point:
    """ Class Points """

    def __init__(self, x: int, y: int) -> None:
        """ constructor for class Point"""
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        """ method of checking for equality """
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        """ str representation method"""
        return f"({self.x}, {self.y})"


class Ship:
    """Class Ships"""

    def __init__(self, bow: Point, l: int, ori: int) -> None:
        """ constructor for class Ship"""
        self.bow = bow
        self.l = l
        self.ori = ori
        self.lives = l

    @property
    def points(self) -> list:
        """method add ship points"""
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.ori == 0:
                cur_x += i
            elif self.ori == 1:
                cur_y += i
            ship_dots.append(Point(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot: Point) -> bool:
        """ method for checking point"""
        return shot in self.points


class Board:
    """Class Board"""

    def __init__(self, hid=False, size=9) -> None:
        """ constructor for class Board """
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def contour(self, ship: Ship, verb=False) -> None:
        """ method that selects an area near the ship, including itself """
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for i in ship.points:
            for ix, iy in near:
                cur = Point(i.x + ix, i.y + iy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "•"
                    self.busy.append(cur)

    def add_ship(self, ship: Ship) -> None:
        """ method for placing a ship on the game board"""

        for i in ship.points:
            if self.out(i) or i in self.busy:
                raise BoardWrongShipException()
        for i in ship.points:
            self.field[i.x][i.y] = "■"
            self.busy.append(i)

        self.ships.append(ship)
        self.contour(ship)

    def __str__(self) -> str:
        """ str representation method"""
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, p: Point) -> bool:
        """ method checking point on the board"""
        return not ((0 <= p.x < self.size) and (0 <= p.y < self.size))

    def shot(self, p: Point) -> bool:
        """ method for making shot"""
        if self.out(p):
            raise BoardOutException()
        if p in self.busy:
            raise BoardUsedException()
        self.busy.append(p)
        for ship in self.ships:
            if p in ship.points:
                ship.lives -= 1
                self.field[p.x][p.y] = "╳"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Уничтожен!")
                    return False
                else:
                    print("Ранен!")
                    return True
        self.field[p.x][p.y] = "•"
        print("Мимо!")
        return False

    def begin(self) -> None:
        """ busy list refresh method """
        self.busy = []


class Player:
    """ Player class"""

    def __init__(self, board: Board, enemy: Board) -> None:
        """ constructor for class Player """
        self.board = board
        self.enemy = enemy

    def ask(self) -> None:
        """ method for child classes """
        raise NotImplementedError()

    def move(self):
        """ method for requesting coordinates and shooting at them"""
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self) -> Point:
        """ method for obtaining random AI shot coordinates """
        p = Point(randint(0, 8), randint(0, 8))
        print(f"Ход Рандомайзера: {p.x + 1} {p.y + 1}")
        return p


class User(Player):
    def ask(self) -> Point:
        """method for obtaining Player's shot coordinates """
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue
            x, y = int(x), int(y)
            return Point(x - 1, y - 1)


class Game:
    """Game class"""

    def __init__(self, size=9):
        """ constructor for class Player """
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        coa = self.random_board()
        cob = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)
        self.aia = AI(coa, cob)
        self.aib = AI(cob, coa)

    def random_place(self) -> Board:
        """ ship board try creation method """
        lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self) -> Board:
        """ship board guaranteed creation method"""
        board = None
        while board is None:
            board = self.random_place()
        return board

    @staticmethod
    def greet() -> None:
        """user greeting method"""
        print("--------------------------------------")
        print("             Приветсвуем              ")
        print("              в игре                  ")
        print("             МОРСКОЙ БОЙ              ")
        print("--------------------------------------")

    @staticmethod
    def rules() -> None:
        """show game rules method"""
        print("--------------------------------------")
        print("Правила игры:")
        print("на игровом поле в случайном порядке")
        print("размещаются:")
        print("1 корабль — ряд из 4 клеток")
        print("2 корабля — ряд из 3 клеток")
        print("3 корабля — ряд из 2 клеток")
        print("4 корабля — 1 клетка")
        print("Потопите корабли противника прежде,  ")
        print("чем он потопит ваши корабли")
        print("--------------------------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
        print("--------------------------------------")

    def loop(self) -> None:
        """game method player versus randomazer"""
        num = 0
        while True:
            print("-" * 40)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 40)
            print("Доска рандомойзера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 40)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 40)
                print("Ходит рандомайзер!")
                sleep(1)
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 10:
                print("-" * 40)
                print("Пользователь выиграл!")
                break
            if self.us.board.count == 10:
                print("-" * 40)
                print("Рандомайзер выиграл!")
                break
            num += 1

    def random_loop(self) -> None:
        """game method randomazer A versus randomazer B"""
        num = 0
        while True:
            print("-" * 40)
            print("Доска Рандомайзера А:")
            print(self.aia.board)
            print("-" * 40)
            print("Доска Рандомайзер Б:")
            print(self.aib.board)
            if num % 2 == 0:
                print("-" * 40)
                print("Ходит Рандомайзер А!")
                sleep(1)
                repeat = self.aia.move()
            else:
                print("-" * 40)
                print("Ходит Рандомайзер Б!")
                sleep(1)
                repeat = self.aib.move()
            if repeat:
                num -= 1
            if self.aib.board.count == 10:
                print("-" * 40)
                print("Рондомайзер А выиграл!")
                break
            if self.aia.board.count == 10:
                print("-" * 40)
                print("Рондомайзер Б выиграл!")
                break
            num += 1

    def chise(self):
        """ mode selection method """
        print("Выберите режим:")
        print("--------------------------------------")
        print("                ( 1 )                 ")
        print("         ИГРОК  против РАНДОМАЙЗЕРА   ")
        print("--------------------------------------")
        print("--------------------------------------")
        print("                ( 2 )                 ")
        print("   РАНДОМАЙЗЕР  против РАНДОМАЙЗЕРА   ")
        print("--------------------------------------")
        while True:
            try:
                you_choise = input('Введите число соответствующее режиму: ')
                print(you_choise)
                if you_choise == '1':
                    self.rules()
                    return self.loop()
                elif you_choise == '2':
                    return self.random_loop()
            except BoardException:
                pass

    def start(self):
        """method for start game"""
        self.greet()
        self.chise()


g = Game()
g.start()
