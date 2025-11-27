from pico2d import *

import random
import math

import common
import game_framework
import game_world
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector


# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

animation_names = ['Walk', 'Idle']


class Zombie:
    images = None

    def load_images(self):
        if Zombie.images == None:
            Zombie.images = {}
            for name in animation_names:
                Zombie.images[name] = [load_image("./zombie/" + name + " (%d)" % i + ".png") for i in range(1, 11)]
            Zombie.font = load_font('ENCR10B.TTF', 40)
            Zombie.marker_image = load_image('hand_arrow.png')


    def __init__(self, x=None, y=None):
        self.x = x if x else random.randint(100, 1180)
        self.y = y if y else random.randint(100, 924)
        self.load_images()
        self.dir = 0.0      # radian 값으로 방향을 표시
        self.speed = 0.0
        self.frame = random.randint(0, 9)
        self.state = 'Idle'
        self.ball_count = 0


        self.tx, self.ty = 1000, 1000
        # 여기를 채우시오.
        self.patrol_points = [(43, 274), (1118, 274), (1050, 494), (575, 804),
                              (235, 991), (575, 804), (1050, 494),(1118, 274)]
        self.loc_no = 0

        self.build_behavior_tree()


    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50


    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        # fill here
        self.bt.run()


    def draw(self):
        if math.cos(self.dir) < 0:
            Zombie.images[self.state][int(self.frame)].composite_draw(0, 'h', self.x, self.y, 100, 100)
        else:
            Zombie.images[self.state][int(self.frame)].draw(self.x, self.y, 100, 100)
        self.font.draw(self.x - 10, self.y + 60, f'{self.ball_count}', (0, 0, 255))
        Zombie.marker_image.draw(self.tx+25, self.ty-25)
        draw_rectangle(*self.get_bb())
        draw_circle(self.x, self.y, int(PIXEL_PER_METER * 7), 255, 255, 0) # 추적 범위 표시

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'zombie:ball':
            self.ball_count += 1


    def set_target_location(self, x=None, y=None):
        # 여기를 채우시오.
        if x is None or y is None:
            raise ValueError("목적지 좌표가 주어지지 않았습니다.")
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS # 목적지 좌표 설명 임무 완료



    def distance_less_than(self, x1, y1, x2, y2, r):
        # 여기를 채우시오.
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 < (PIXEL_PER_METER * r) ** 2
        # r은 미터 단위이기 때문에 픽셀 단위로 변환해야함.

    def distance_more_than(self, x1, y1, x2, y2, r):
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 > (PIXEL_PER_METER * r) ** 2

    def move_little_to(self, tx, ty):
        # dir : 각도, atan2 : 탄젠트의 역수, 역함수 (분자, 분모)
        self.dir = math.atan2(ty - self.y, tx - self.x)
        distance = game_framework.frame_time * RUN_SPEED_PPS
        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)
        pass



    def move_to(self, r=0.5):
        # 여기를 채우시오.
        self.state = "Walk"
        self.move_little_to(self.tx, self.ty)
        # 좀비가 목적지에 도착했는지 검사
        if self.distance_less_than(self.tx, self.ty, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING



    def set_random_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = random.randint(0, 800), random.randint(0, 600)
        return BehaviorTree.SUCCESS


    def if_boy_nearby(self, distance):
        # 여기를 채우시오.
        if self.distance_less_than(self.x, self.y, common.boy.x, common.boy.y, distance):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def if_less_than_balls(self):
        if self.ball_count >= common.boy.ball_count:
            return BehaviorTree.FAIL
        else:
            return BehaviorTree.SUCCESS


    def move_to_boy(self, r=0.5):
        # 여기를 채우시오.
        self.state = 'Walk'
        # 소년 쪽으로 살짝 이동
        self.move_little_to(common.boy.x, common.boy.y)
        # 좀비가 소년에게 도착했는지 검사
        if self.distance_less_than(self.x, self.y, common.boy.x, common.boy.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING


    def get_patrol_location(self): # 다음 순찰 위치 획득
        # 여기를 채우시오.
        self.tx , self.ty = self.patrol_points[self.loc_no]
        self.loc_no = (self.loc_no + 1) % len(self.patrol_points)
        return BehaviorTree.SUCCESS

    def run_from_boy(self, r=7):
        self.state = 'Walk'
        # 소년 반대쪽으로 살짝 이동
        self.tx, self.ty = self.x + (self.x - common.boy.x), self.y + (self.y - common.boy.y)
        self.move_little_to(self.tx, self.ty)
        # 좀비가 소년에게서 벗어났는지 검사
        if self.distance_more_than(self.x, self.y, common.boy.x, common.boy.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING


    def build_behavior_tree(self):
        # 여기를 채우시오.
        # 노드 만들기 Action : 노드의 기능 , "목적지 설정" : 노드 이름, self.set_target_location : 노드가 실행할 함수
        a1 = Action("목적지 설정", self.set_target_location, 600, 400)
        a2 = Action("목적지로 이동", self.move_to)
        move_to_target_location = Sequence("지정된 목적지로 이동", a1, a2)

        a3 = Action("랜덤 목적지 설정", self.set_random_location)
        wander = Sequence("목적지 없이 배회", a3, a2)

        c1 = Condition('소년이 근처에 있는가', self.if_boy_nearby, 7)
        a4 = Action('소년 추적', self.move_to_boy)
        chase_boy_if_nearby = Sequence('소년이 근처에 있으면 추적', c1, a4)

        chase_or_wander = Selector('추적 아니면 배회', chase_boy_if_nearby, wander)

        a5 = Action('다음 순찰 위치 획득', self.get_patrol_location)
        patrol = Sequence('순찰', a5, a2)

        chase_or_patrol = Selector('추적 아니면 순찰', chase_boy_if_nearby, patrol)

        c2 = Condition('소년보다 공이 더 적은가', self.if_less_than_balls)
        a6 = Action('소년에게서 도망', self.run_from_boy)
        runaway = Sequence('소년보다 공이 더 적으면 도망', c2, a6)
        chase_or_runaway = Selector('추적 아니면 도망', runaway, a4)
        competition = Sequence('추적 아니면 도망', c1, chase_or_runaway)

        root = competition_or_wander = Selector('경쟁 아니면 배회', competition, wander)
        self.bt = BehaviorTree(root)
        pass


