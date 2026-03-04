import pygame
from settings import Settings
from time import sleep
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
import sys
class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.clock=pygame.time.Clock()
        self.settings = Settings()
        self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.settings.screen_width=self.screen.get_rect().width
        self.settings.screen_height=self.screen.get_rect().height
        self.stats=GameStats(self)
        self.ship=Ship(self)
        self.game_active=False
        self.pause=False
        self.z=False
        self.v=False
        self.b=False
        self.play_button=Button(self,"Play")
        self.sb = Scoreboard(self)
        self.bullets=pygame.sprite.Group()
        self.aliens=pygame.sprite.Group()
        self.auto_fire=False
        self.f=0
        self._create_fleet()
        pygame.display.set_caption("Alien Invasion")
    def run_game(self):
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                if self.v:
                    self.f += 1
                    if self.auto_fire and self.f % 3 == 0:
                        self._fire_bullet()
                        self.f %=3
            self._update_screen()
            self.clock.tick(60)
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos=pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
    def _check_play_button(self,mouse_pos):
        button_clicked= self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active and not self.pause:
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active=True
            self.settings.initialize_dynamic_settings()
            self.bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)
    def _check_keydown_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        if event.key == pygame.K_ESCAPE:
            sys.exit()
        if event.key == pygame.K_z:
            self.z=True
        if event.key == pygame.K_x:
            self.stats.ships_left += 3
            self.sb.prep_ships()
        if event.key == pygame.K_c:
            self.aliens.empty()
        if event.key == pygame.K_v:
            self.v=True
        if event.key == pygame.K_t:
            self.z=False
            self.v=False
        if event.key == pygame.K_SPACE:
            self._fire_bullet()
            if self.v:
                self.auto_fire=True
        if event.key == pygame.K_m:
            if self.game_active:
                self.play_button = Button(self, "Stop")
                self.game_active=False
                self.pause=True
            else:
                self.play_button = Button(self, "Play")
                self.game_active=True
                self.pause=False
    def _check_keyup_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        if event.key == pygame.K_SPACE:
            if self.v:
                self.auto_fire=False
    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()
    def _check_bullet_alien_collisions(self):
        if self.z:
            collisions=pygame.sprite.groupcollide(self.aliens,self.bullets,True,False)
        else:
            collisions=pygame.sprite.groupcollide(self.aliens,self.bullets,True,True)
        if collisions:
            for alien in collisions.values():
                self.stats.score+=self.settings.alien_points*len(alien)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level+=1
            self.sb.prep_level()
    def _fire_bullet(self):
        if len(self.bullets) <= self.settings.bullets_allowed:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)
    def _create_fleet(self):
        alien=Alien(self)
        self.aliens.add(alien)
        alien_width,alien_height=alien.rect.size
        current_x,current_y=alien_width,alien_height
        while current_y<self.settings.screen_height-3*alien_height:
            while current_x < (self.settings.screen_width -2*alien_width):
                self._create_alien(current_x,current_y)
                current_x+=2*alien_width
            current_x=alien_width
            current_y+=2*alien_height
    def _create_alien(self,x_positions,y_positions):
        new_alien = Alien(self)
        new_alien.x = x_positions
        new_alien.rect.x = new_alien.x
        new_alien.rect.y = y_positions
        self.aliens.add(new_alien)
    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y+=self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()
        self._check_aliens_bottom()
    def _ship_hit(self):
        if self.stats.ships_left>1:
            self.stats.ships_left-=1
            self.sb.prep_ships()
            self.bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.stats.reset_stats()
            self.game_active=False
            pygame.mouse.set_visible(True)
    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >=self.settings.screen_height:
                self._ship_hit()
                break
    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.game_active:
            if not self.pause:
                self.play_button.draw_button()
            if self.pause:
                self.play_button.draw_button()
        pygame.display.flip()
if __name__ == "__main__":
    ai=AlienInvasion()
    ai.run_game()