"""Infinitely scrolling dino game.
"""
import itertools
import time
import arcade

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(":resources:images/animated_characters/female_person/femalePerson_idle.png")
        self.scale = 0.5
        self.vel_x = 300
        self.vel_y = 0

class Cactus(arcade.Sprite):
    def __init__(self, **kwargs):
        super().__init__(":resources:images/tiles/cactus.png", **kwargs)
        self.scale = 0.5

class Ground(arcade.Sprite):
    def __init__(self, **kwargs):
        super().__init__(":resources:images/tiles/grassMid.png", **kwargs)
        self.scale = 0.5


class DinoGame(arcade.View):
    ground_y = 50
    gravity = 2000
    player_near_ground = 10
    jump_strength = 700
    cactus_spawn_distance = 300

    def __init__(self, high_score=0):

        super().__init__()
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.player = Player()
        self.player.bottom = self.ground_y + 200
        self.player_group = arcade.SpriteList()
        self.player_group.append(self.player)

        self.ground_list = arcade.SpriteList()
        ground = Ground()
        ground.left = -500
        ground.top = self.ground_y
        self.ground_list.append(ground)

        self.cactus_list = arcade.SpriteList()
        self.score_list = arcade.SpriteList()

        self.score = 0
        self.high_score = high_score
        self.start_time = time.time()
        self.text_stats = arcade.Text("", 10, self.height - 10, anchor_y="top")
        self.text_instructions = arcade.Text(
            "Commands:\nP = Play/Pause toggle\nR = Restart\nSPACE = Jump\nESC = Quit\nD = Debug toggle",
            self.width / 2, self.height / 2, width=300, multiline=True, font_size=15,
            anchor_x="center", anchor_y="center",
        )

        self.camera = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()

        self.paused = True
        self.debug = True

        self.sound_jump = arcade.Sound(":resources:sounds/jump1.wav")
        self.sound_hurt = arcade.Sound(":resources:sounds/hurt1.wav")
        self.music = arcade.Sound(":resources:music/funkyrobot.mp3")
        self.music_player = self.music.play(loop=True)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            if self.player.bottom - self.ground_y < self.player_near_ground:
                self.player.vel_y += self.jump_strength
                self.sound_jump.play()
        if key == arcade.key.P:
            self.paused = not self.paused
        if key == arcade.key.D:
            self.debug = not self.debug
        if key == arcade.key.R:
            self.window.show_view(self.__class__())
        if key == arcade.key.ESCAPE:
            self.window.close()

    def on_update(self, delta_time):
        self.spawn_new()
        self.delete_old()
        self.camera.position = (self.player.left + 200, self.camera.position[1])

        self.text_stats.text = (
            f"Score: {self.score:3d}   "
            f"High score: {self.high_score:3d}   "
            f"Time: {time.time() - self.start_time:5.2f}"
        )

        if self.paused:
            return

        self.update_player(delta_time)

        for score_sprite in arcade.check_for_collision_with_list(self.player, self.score_list):
            self.score += 1
            score_sprite.remove_from_sprite_lists()

        # Cactus collision - immediate game over and restart to instruction screen.
        if arcade.check_for_collision_with_list(self.player, self.cactus_list):
            self.high_score = max(self.score, self.high_score)
            self.sound_hurt.play()
            self.music_player.delete()
            self.window.show_view(self.__class__(high_score=self.high_score))


    def update_player(self, delta_time):
        self.player.vel_y -= self.gravity * delta_time # gravity
        self.player.center_x += delta_time * self.player.vel_x
        self.player.center_y += delta_time * self.player.vel_y
        if self.player.bottom < self.ground_y:
            self.player.bottom = self.ground_y
            self.player.vel_y = 0

    def spawn_needed(self):
        return self.camera.project(self.ground_list[-1].position).x < self.width

    def spawn_new(self):
        while self.spawn_needed():
            g = self.ground_list[-1]
            sprite = Ground(
                center_x=g.center_x + g.width + 2,
                center_y=g.center_y,
            )
            self.ground_list.append(sprite)

            if len(self.cactus_list) > 0:
                distance = g.left - self.cactus_list[-1].right
            else:
                distance = 1000

            if distance > self.cactus_spawn_distance:
                sprite = Cactus(center_x=g.center_x)
                sprite.bottom = self.ground_y
                self.cactus_list.append(sprite)

                score_box = arcade.SpriteSolidColor(
                    width=sprite.width,
                    height=sprite.height * 3,
                    center_x=sprite.center_x,
                )
                score_box.bottom = sprite.top
                self.score_list.append(score_box)

    def delete_old(self):
        for g in itertools.chain(self.ground_list, self.cactus_list, self.score_list):
            if g.right < self.camera.position.x - self.width:
                g.remove_from_sprite_lists()

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.ground_list.draw()
        self.cactus_list.draw()
        self.player_group.draw()

        if self.debug:
            self.cactus_list.draw_hit_boxes(arcade.color.RED, 2)
            self.score_list.draw_hit_boxes(arcade.color.RED, 2)
            self.player.draw_hit_box(arcade.color.RED, 2)

        self.camera_gui.use()
        self.text_stats.draw()
        if self.paused:
            self.text_instructions.draw()


def main():
    window = arcade.Window(800, 400, "Dino Game")
    window.show_view(DinoGame())
    arcade.run()


main()
