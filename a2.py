from a2_support import *


class GameApp(object):
    """
    # GameApp类作为传递GameLogic类和Display类之间通信的类
    """
    def __init__(self):
        """
        初始化
        """
        self.gamelogic = GameLogic()
        self.display = Display(self.gamelogic.get_game_information(), self.gamelogic.get_dungeon_size())

    def play2(self, direction):
        """
        具体交互逻辑
        :param direction:
        :return:
        """
        # 检查指定方向是否有实体
        if not self.gamelogic.collision_check(direction):
            # 不会碰到实体 可能没有实体 或实体是道具
            entity = self.gamelogic.get_entity_in_direction(direction)
            if not entity:
                # 没有实体 直接移动
                self.gamelogic.move_player(direction)
            else:
                # 道具 钥匙 或 门
                entity.on_hit(self.gamelogic)
                self.gamelogic.move_player(direction)
        else:
            # 墙
            print(INVALID)
        # 玩家步数+1
        self.gamelogic.get_player().max_move_count = self.gamelogic.get_player().max_move_count - 1

    def play(self):
        """
        处理玩家交互
        :param direction:
        :return:
        """
        # 游戏是否结束标识
        game_is_over = False
        while not game_is_over:
            # 绘制地牢图形和用户剩余步数
            self.draw()
            # 提示用户输入
            user_input = input("Please input an action: ")
            user_input_list = user_input.split(" ")
            # 输入检查
            while user_input_list[0] not in VALID_ACTIONS or len(user_input_list) > 2 or (
                    len(user_input_list) > 1 and not user_input_list[0] == INVESTIGATE):
                print(INVALID)
                self.draw()
                # 提示用户输入
                user_input = input("Please input an action: ")
                user_input_list = user_input.split(" ")
            # 调查给定方向的实体
            if user_input_list[0] == INVESTIGATE:
                direction = user_input_list[1]
                if direction not in list(DIRECTIONS.keys()):
                    print(INVALID)
                else:
                    entity = self.entity_in_direction(direction)
                    print("{} is on the {} side.".format(entity, direction))
                    self.gamelogic.get_player().max_move_count = self.gamelogic.get_player().max_move_count - 1
            # 帮助信息
            elif user_input_list[0] == HELP:
                print(HELP_MESSAGE)
            # 退出游戏
            elif user_input_list[0] == QUIT:
                is_exit = input("Are you sure you want to quit? (y/n): ")
                if is_exit == "y":
                    game_is_over = True
                    break
            # 玩家移动
            else:
                self.play2(user_input_list[0])
            # 检查游戏是否赢了
            if self.gamelogic.won():
                game_is_over = True
                print(WIN_TEXT)
                break
            # 检查游戏是否结束
            if self.gamelogic.check_game_over():
                game_is_over = True
                print(LOSE_TEST)
                break

    def entity_in_direction(self, direction):
        """
        # 返回在给定方向上的实体
        :param direction:
        :return:
        """
        return self.gamelogic.get_entity_in_direction(direction)

    def draw(self):
        """
        # 展示包含所有地牢中实体及其所在位置，同时也应展示玩家剩余的步数
        :return:
        """
        self.display.display_game(self.gamelogic.get_player().get_position())
        self.display.display_moves(self.gamelogic.get_player().moves_remaining())


class GameLogic(object):
    """
    # GameLogic类包含所有的游戏信息和游戏该怎么玩
    """
    def __init__(self, dungeon_name="game1.txt"):
        """Constructor of the GameLogic class.

        Parameters:
            dungeon_name (str): The name of the level.
        """
        # 地牢二维数组
        self._dungeon = load_game(dungeon_name)
        # 地牢宽度
        self._dungeon_size = len(self._dungeon)
        # 玩家
        self._player = Player(GAME_LEVELS[dungeon_name])
        # 地牢所有实体位置
        self._game_information = self.init_game_information()
        # 玩家输赢
        self._win = False

    def get_positions(self, entity):
        """ Returns a list of tuples containing all positions of a given Entity
             type.
        # 返回给定实体在地牢中的位置
        Parameters:
            entity (str): the id of an entity.

        Returns:
            )list<tuple<int, int>>): Returns a list of tuples representing the
            positions of a given entity id.
        """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def get_dungeon_size(self):
        """
        # 获取地牢的宽
        :return:
        """
        return self._dungeon_size

    def init_game_information(self):
        """
        # 返回一个包含位置和对应实体作为键值对的字典
        :return:
        """
        res = {}
        for i in range(len(self._dungeon)):
            for j in range(len(self._dungeon[i])):
                if self._dungeon[i][j] == "#":
                    entity = Wall()
                    res.update({
                        (i, j): entity
                    })
                elif self._dungeon[i][j] == "K":
                    entity = Key()
                    res.update({
                        (i, j): entity
                    })
                elif self._dungeon[i][j] == "M":
                    entity = MoveIncrease()
                    res.update({
                        (i, j): entity
                    })
                elif self._dungeon[i][j] == "D":
                    entity = Door()
                    res.update({
                        (i, j): entity
                    })
                elif self._dungeon[i][j] == "O":
                    self._player.set_position((i, j))
        return res

    def get_game_information(self):
        """
        # 返回一个包含位置和对应实体作为键值对的字典
        :return:
        """
        return self._game_information

    def get_player(self):
        """
         # 返回游戏的Player对象
        :return:
        """
        return self._player

    def get_entity(self, position):
        """
        # 返回实体在当前地牢的给定位置，实体在给定方向或者位置在地牢外这个方法应该返回None
        :param position:
        :return:
        """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """
         返回一个包含用户给定位置的实体，如果给定方向没有实体或在地牢外这个方法应返回None
        :param direction:
        :return:
        """
        row, colum = self._player.get_position()
        if direction == 'W':
            row = row - 1
        elif direction == 'S':
            row = row + 1
        elif direction == 'A':
            colum = colum - 1
        elif direction == 'D':
            colum = colum + 1
        return self._game_information.get((row, colum))

    def collision_check(self, direction):
        """
        # 当用户沿给定方向前进并不会碰到实体时返回False，否则返回True
        :param direction:
        :return:
        """
        row, colum = self._player.get_position()
        if direction == 'W':
            row = row - 1
        elif direction == 'S':
            row = row + 1
        elif direction == 'A':
            colum = colum - 1
        elif direction == 'D':
            colum = colum + 1
        if not self._game_information.get((row, colum)):
            # 没有实体
            return False
        if self._game_information.get((row, colum)).can_collide():
            # 可被碰撞的实体 钥匙 门 道具等
            return False
        return True

    def new_position(self, direction):
        """
        # 返回一个包含沿给定方向的新位置的元组
        :param direction:
        :return:
        """
        row, colum = self._player.get_position()
        if direction == 'W':
            row = row - 1
        elif direction == 'S':
            row = row + 1
        elif direction == 'A':
            colum = colum - 1
        elif direction == 'D':
            colum = colum + 1
        return row, colum

    def move_player(self, direction):
        """
        # 根据给定的方向更新玩家的位置
        :param direction:
        :return:
        """
        row, colum = self._player.get_position()
        if direction == 'W':
            row = row - 1
        elif direction == 'S':
            row = row + 1
        elif direction == 'A':
            colum = colum - 1
        elif direction == 'D':
            colum = colum + 1
        self._player.set_position((row, colum))

    def check_game_over(self):
        """
        # 检查游戏是否结束 如果结束了返回True 否则返回False
        :return:
        """
        if self._win or self.get_player().moves_remaining() < 1:
            return True
        else:
            return False

    def set_win(self, win):
        """
        # 设置游戏胜利状态为True或者False
        :param win:
        :return:
        """
        self._win = win

    def won(self):
        """
        # 返回游戏是否胜利
        :return:
        """
        return self._win


class Entity(object):
    """
    # 实体类
    """
    def __init__(self):
        """
        初始化
        """
        self.collidable = True

    def get_id(self):
        """
        获取ID
        :return:
        """
        return "Entity"

    def set_collide(self, collidable):
        """
        设置是否可碰撞
        :param collidable:
        :return:
        """
        self.collidable = collidable

    def can_collide(self):
        """
        是否可碰撞
        :return:
        """
        return self.collidable

    def __str__(self):
        """
        打印
        :return:
        """
        return "Entity('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Entity('{}')".format(self.get_id())


class Wall(Entity):
    """
    # 墙
    """
    def __init__(self):
        """
        初始化
        """
        self.collidable = False

    def get_id(self):
        """
        获取ID
        :return:
        """
        return "#"

    def __str__(self):
        """
        打印
        :return:
        """
        return "Wall('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Wall('{}')".format(self.get_id())


class Item(Entity):
    """
    # 抽象子类
    """
    def on_hit(self, game):
        """
        碰撞
        :param game:
        :return:
        """
        raise NotImplementedError

    def __str__(self):
        """
        打印
        :return:
        """
        return "Item('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Item('{}')".format(self.get_id())


class Key(Item):
    """
    # 解锁门
    """
    def get_id(self):
        """
        获取ID
        :return:
        """
        return "K"

    def on_hit(self, game):
        """
        # 玩家拿到钥匙 钥匙添加到玩家的存货中 并从地图中移除
        :param game:
        :return:
        """
        # 道具放入玩家背包
        game.get_player().add_item(self)
        # 从地图中删除 TODO 只允许存在一个K 否则会全部删除
        positions = game.get_positions('K')
        del game.get_game_information()[positions[0]]

    def __str__(self):
        """
        打印
        :return:
        """
        return "Key('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Key('{}')".format(self.get_id())


class MoveIncrease(Item):
    """
    # 增加用户步数的道具
    """
    def __init__(self, moves=5):
        """
        初始化
        :param moves:
        """
        super().__init__()
        self.moves = moves

    def get_id(self):
        """
        获取ID
        :return:
        """
        return "M"

    def on_hit(self, game):
        """
            # 玩家拿到此道具 物品添加到玩家的存货中 并从地图中移除 玩家步数增加指定的值
        :param game:
        :return:
        """
        # 玩家增加步数
        game.get_player().change_move_count(self.moves)
        # 道具放入玩家背包
        game.get_player().add_item(self)
        # 从地图中删除 TODO 只允许存在一个M 否则会全部删除
        positions = game.get_positions('M')
        del game.get_game_information()[positions[0]]

    def __str__(self):
        """
        打印
        :return:
        """
        return "MoveIncrease('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "MoveIncrease('{}')".format(self.get_id())


class Door(Entity):
    """
    # 允许玩家离开的门
    """
    def get_id(self):
        """
        获取ID
        :return:
        """
        return "D"

    def __str__(self):
        """
        打印
        :return:
        """
        return "Door('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Door('{}')".format(self.get_id())

    def on_hit(self, game):
        """
            # 当玩家有key时 游戏结束 没有key 提示You don’t have the key!
        :param game:
        :return:
        """
        products = game.get_player().get_inventory()
        is_has_key = False
        for product in products:
            if isinstance(product, Key):
                is_has_key = True
        if is_has_key:
            game.set_win(True)
        else:
            print("You don't have the key!")


class Player(Entity):
    """
    # 玩家
    """
    def __init__(self, max_movies):
        """
        初始化
        :param max_movies:
        """
        super().__init__()
        # 当前位置
        self.position = None
        # 最大可移动步数
        self.max_move_count = max_movies
        # 持有的物品
        self.product = []

    def get_id(self):
        """
        ID
        :return:
        """
        return "O"

    def __str__(self):
        """
        打印
        :return:
        """
        return "Player('{}')".format(self.get_id())

    def __repr__(self):
        """
        打印
        :return:
        """
        return "Player('{}')".format(self.get_id())

    def set_position(self, position):
        """
        # 设置Player的位置
        :param position:
        :return:
        """
        self.position = position

    def get_position(self):
        """
        # 设置Player的位置
        :return:
        """
        return self.position

    def change_move_count(self, number):
        """
            # 玩家捡到道具M 增加的步数
        :param number:
        :return:
        """
        self.max_move_count = self.max_move_count + number

    def moves_remaining(self):
        """
            # 返回代表玩家达到最大允许步数前的剩余步数
        :return:
        """
        return self.max_move_count

    def add_item(self, item):
        """
            # 给玩家的库存添加物品
        :param item:
        :return:
        """
        self.product.append(item)

    def get_inventory(self):
        """
            # 返回一个代表玩家库存的列表，如果玩家库存为空，返回一个空列表
        :return:
        """
        return self.product


def main():
    """
    # 主函数
    :return:
    """
    game_app = GameApp()
    game_app.play()


# def entity_test():
#     entity = Entity()
#     print(entity.get_id())
#     print(entity.can_collide())
#     print(entity)
#     print(repr(entity))
#     entity.set_collide(False)
#     print(entity.can_collide())
#
#
# def wall_test():
#     wall = Wall()
#     print(wall.get_id())
#     print(wall.can_collide())
#     print(wall)
#     print(repr(wall))
#     wall.set_collide(True)
#     print(wall.can_collide())
#
#
# def item_test():
#     game = GameLogic()
#     item = Item()
#     print(item.get_id())
#     print(item.can_collide())
#     print(item)
#     print(repr(item))
#     print(item.on_hit(game))
#
#
# def moveIncrease_test():
#     move = MoveIncrease()
#     print(move.get_id())
#     print(move.can_collide())
#     print(move)
#     print(repr(move))
#     game = GameLogic("game3.txt")
#     print(game.get_game_information())
#     player = game.get_player()
#     player.set_position((6, 6))
#     print(player.moves_remaining())
#     move.on_hit(game)
#     print(player.moves_remaining())
#     print(game.get_game_information())
#
#
# def door_test():
#     door = Door()
#     print(door.get_id())
#     print(door.can_collide())
#     print(door)
#     print(repr(door))
#     key = Key()
#     game = GameLogic()
#     print(game.get_game_information())
#     player = game.get_player()
#     print(game.won())
#     player.set_position((3, 2))
#     door.on_hit(game)
#     print(player.get_inventory())
#     player.set_position((1, 3))
#     player.add_item(key)
#     door.on_hit(game)
#     print(player.get_inventory())
#     print(game.won())
#
#
# def player_test():
#     player = Player(5)
#     print(player.get_position())
#     player.set_position((1, 2))
#     print(player.get_position())
#     print(player.moves_remaining())
#     print(player.get_inventory())
#     key = Key()
#     player.add_item(key)
#     print(player.get_inventory())
#     print(player)
#     print(repr(player))
#
#
# def gamelogic_test():
#     game = GameLogic()
#     print(game.get_positions(PLAYER))
#     print(game.init_game_information())
#     print(game.get_player())
#     print(game.get_positions(KEY))
#     print(game.get_entity((2, 1)))
#     print(game.get_entity((1, 3)))
#     print(game.get_entity_in_direction("W"))
#     print(game.get_entity_in_direction("D"))
#     print(game.get_entity_in_direction("A"))
#     print(game.get_game_information())
#     print(game.get_dungeon_size())
#     print(game.get_player().get_position())
#     print(game.move_player("W"))
#     print(game.get_player().get_position())
#     print(game.collision_check("W"))
#     print(game.collision_check("S"))
#     print(game.new_position("W"))
#     print(game.new_position("S"))
#     print(game.check_game_over())
#     print(game.won())
#     game.set_win(True)
#     print(game.won())


if __name__ == "__main__":
    # entity_test()
    # wall_test()
    # item_test()
    # moveIncrease_test()
    # door_test()
    # player_test()
    # gamelogic_test()
    main()