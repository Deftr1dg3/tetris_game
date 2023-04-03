#!/usr/bin/env python3


import wx
import random


# Use "z" button to rotate the figure left
# Use "q" to change the figure in the beginning.
# Use "b" to write on board current situation.

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Tetris1.0', size=(400, 656),
                          style=wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.STAY_ON_TOP)
        self.InitUI()
        self.SetPosition((800, -1))

    def InitUI(self):

        self.panel = wx.Panel(self)
        self.panel.SetFocus()

        self.statusbar = self.CreateStatusBar(3)

        self.score = 0
        self.level = 1
        self.lives = 3

        self.statusbar.SetStatusText('Score: ' + str(self.score), 0)
        self.statusbar.SetStatusText('Level: ' + str(self.level), 1)
        self.statusbar.SetStatusText('Lives: ' + str(self.lives), 2)

        self.square_side = 20

        self.timer_speed = 600

        self.paused = False

        self.display_width = self.GetClientSize().GetWidth() // self.square_side
        self.display_height = self.GetClientSize().GetHeight() // self.square_side

        self.start_x = (self.GetClientSize().GetWidth() // self.square_side) // 2
        self.start_y = 1

        self.score = 0

        self.x = self.start_x
        self.y = self.start_y

        self.coords = self.setShape()

        self.on_board = [[0] * self.display_width for i in range(self.display_height)]

        self.timer = wx.Timer(self)
        self.timer.Start(self.timer_speed)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnPaint(self, e):

        dc = wx.PaintDC(self)

        for r in range(self.display_height):
            for i in range(self.display_width):
                if self.on_board[r][i] != 0:
                    shape = self.on_board[r][i]
                    self.drawRectangle(dc, i, r, shape)

        for coord in self.coords:
            x = self.x + coord[0]
            y = self.y + coord[1]
            self.drawRectangle(dc, x, y, self.shape)

    def OnKeyDown(self, e):

        code = e.GetKeyCode()

        if code == ord('Z'):
            self.rotateLeft()
        elif code == 314:
            self.try_to_Move(self.x - 1, self.y)
        elif code == 316:
            self.try_to_Move(self.x + 1, self.y)
        elif code == 315:
            self.try_to_Move(self.x, self.y - 1)
        elif code == 317:
            self.try_to_Move(self.x, self.y + 1)

        elif code == ord('Q'):
            self.newPiece()

        elif code == ord('B'):
            self.writeOnBoard()

        elif code == wx.WXK_SPACE:
            self.paused = not self.paused
            if self.paused:
                self.timer.Stop()
            else:
                self.timer.Start(self.timer_speed)

        elif code == wx.WXK_ESCAPE:
            self.Close()

        self.Refresh()

    def OnTimer(self, e):

        self.lineDown()

    def try_to_Move(self, x, y):

        for coord in self.coords:
            a, b = coord[0], coord[1]

            new_x = x + a
            new_y = y + b

            if new_x < 0 or new_x >= self.display_width or new_y < 0 or new_y >= self.display_height:
                return False

            if self.on_board[new_y][new_x] != 0:
                return False

        self.x = x
        self.y = y

        self.Refresh()

        return True

    def newPiece(self):

        self.coords = self.setShape()
        self.x = self.start_x
        self.y = self.start_y

        if not self.try_to_Move(self.x, self.y + 1):
            self.timer.Stop()
            if self.lives == 0:
                self.SetTitle('You Lost')
                dial = wx.MessageDialog(None, 'Do you with to try again?',
                                        f'You lost\nFinal score: {self.score}', wx.YES_NO)
                res = dial.ShowModal()
                if res == wx.ID_YES and self.lives > 0:
                    self.clearOnBoard()
                else:
                    self.Destroy()
            else:
                self.lives -= 1
                if self.lives == 0:
                    wx.MessageBox('Notification', 'This is the last live')
                else:
                    wx.MessageBox('Notification', f'You have {self.lives} more lives left')
                self.clearOnBoard()
                self.timer_speed = 600
                self.statusbar.SetStatusText('Lives: ' + str(self.lives), 2)

        self.Refresh()

    def clearOnBoard(self):
        for r in range(self.display_height):
            for i in range(self.display_width):
                self.on_board[r][i] = 0
        self.score = 0
        self.newPiece()
        self.timer.Start(self.timer_speed)
        self.Refresh()

    def lineDown(self):
        if not self.try_to_Move(self.x, self.y + 1):
            self.pieceDropped()

    def pieceDropped(self):
        self.writeOnBoard()

    def writeOnBoard(self):

        for coord in self.coords:
            i = self.x + coord[0]
            r = self.y + coord[1]
            try:
                self.on_board[r][i] = self.shape
            except IndexError:
                pass

        self.removeLine()
        self.newPiece()

    def removeLine(self):
        self.timer.Stop()

        i = self.display_width
        for r in range(len(self.on_board)):
            if 0 not in self.on_board[r]:
                del self.on_board[r]
                self.on_board = [[0] * self.display_width] + self.on_board
                self.score += i
                self.statusbar.SetStatusText('Score: ' + str(self.score), 0)

        self.progress()

        self.timer.Start(self.timer_speed)

    def progress(self):
        ind = self.display_width
        if self.score > 0 and self.score % (ind * self.level) == 0:
            self.level += 1
            self.statusbar.SetStatusText('Level: ' + str(self.level), 1)

    def drawRectangle(self, dc, x, y, shape):

        colours = ('#000000', '#FBF716', '#164EFB', '#FB4116', '#4DFB16',
                   '#FB16EA', '#16FBF6', '#D5057F'
                   )

        dc.SetPen(wx.Pen(wx.Colour(32, 32, 32)))
        dc.SetBrush(wx.Brush(colours[shape]))

        dc.DrawRectangle(x * self.square_side, y * self.square_side,
                         self.square_side, self.square_side)

    def rotateLeft(self):

        if self.shape == 3:
            return

        new = self.coords[:]

        if self.shape == 2:
            for coord in new:
                coord[0], coord[1] = coord[1], coord[0]
        else:
            for coord in new:
                coord[0], coord[1] = coord[1], -coord[0]

        self.coords = new
        self.Refresh()

    def setShape(self):

        coords_list = [
            [[0, 0], [0, 0], [0, 0], [0, 0]],
            [[0, -1], [0, 0], [0, 1], [-1, 0]],
            [[0, -1], [0, 0], [0, 1], [0, 2]],
            [[0, 0], [0, 1], [1, 0], [1, 1]],
            [[-1, -1], [0, -1], [0, 0], [1, 0]],
            [[-1, 0], [0, 0], [0, -1], [1, -1]],
            [[0, -1], [0, 0], [0, 1], [1, 1]],
            [[0, -1], [0, 0], [0, 1], [-1, 1]]

        ]

        self.shape = random.randint(1, 7)
        return coords_list[self.shape]


# ----------------------------------Launch the game---------------------------------------------------


def main():
    app = wx.App()
    Frame().Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
