import sys
import logging
import colorlog
import random
import ctypes

from PySide6.QtWidgets import (
	QWidget,
	QMainWindow,
	QApplication,
	QSpacerItem,
	QVBoxLayout,
	QSizePolicy,
	QPushButton,
	QLabel,
	QHBoxLayout,
	QRadioButton,
	QGraphicsView,
	QStatusBar,
	QGraphicsScene
)
from PySide6.QtGui import (
	QIcon,
	QPixmap,
	QCloseEvent
)
from PySide6.QtCore import (
	Qt,
	QSettings,
	QRect,
	QRectF,
	QTimer
)

from enums import *
import resources

# ----- logging setup -----
MISC = 1

log_colors = {
	'MISC': 'white',
	'DEBUG': 'green',
	'INFO': 'blue',
	'WARNING': 'yellow',
	'ERROR': 'red',
	'CRITICAL': 'bold_red'
}

logger = logging.getLogger(__name__)
logger.propagate = False

formatter = colorlog.ColoredFormatter(
	fmt="${log_color}${name} [level ${levelno} ${levelname} ${asctime}, line ${lineno} in ${filename}"
	    " | Thread ${thread} (${threadName}) Process ${process} (${processName})] ${message}",
	datefmt="%Y/%m/%d %I:%M:%S %p",
	style="$",
	log_colors=log_colors
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(MISC)

logger.addHandler(handler)
logging.addLevelName(MISC, 'MISC')
logger.setLevel(MISC)


# ----- window -----
class UIMainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		tr = self.tr

		self.paper = QPixmap(":/icons/paper")
		self.rock = QPixmap(":/icons/rock")
		self.scissors = QPixmap(":/icons/scissors")

		self.opponentmove = Moves.NoMove
		self.playermove = Moves.NoMove

		self.rounds_played = 0
		self.wins = 0
		self.losses = 0
		self.draws = 0

		self.playtime = 0

		self.settings = QSettings("nonimportant", "rock_paper_scissors", self)

		if not self.settings.contains('total_play_time'):
			self.settings.setValue('total_play_time', 0)

		if not self.settings.contains('total_rounds'):
			self.settings.setValue('total_rounds', 0)

		if not self.settings.contains('total_wins'):
			self.settings.setValue('total_wins', 0)

		if not self.settings.contains('total_losses'):
			self.settings.setValue('total_losses', 0)

		if not self.settings.contains('total_draws'):
			self.settings.setValue('total_draws', 0)

		self.setWindowTitle(tr("Rock Paper Scissors!"))
		self.setGeometry(
			self.settings.value("last_geometry") if self.settings.value("last_geometry") else QRect(550, 250, 875, 610)
		)

		self.centralwidget = QWidget(self)

		self.verticalLayout = QVBoxLayout(self.centralwidget)

		timr = QTimer(self)
		timr.timeout.connect(
			lambda: self.settings.setValue("total_play_time", self.settings.value("total_play_time") + 1)
		)
		timr.timeout.connect(self.increment)
		timr.start(1000)

		self.scene = QGraphicsScene(self)

		self.graphicsView = QGraphicsView(self.scene)
		self.graphicsView.setVerticalScrollBar(None)
		self.graphicsView.setToolTip(tr("Your opponent"))
		self.verticalLayout.addWidget(self.graphicsView)

		spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.verticalLayout.addItem(spacer_item)

		self.newsfeed = QLabel(tr(""), self.centralwidget)
		self.newsfeed.setAlignment(Qt.AlignCenter)
		self.verticalLayout.addWidget(self.newsfeed)

		spacer_item1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)
		self.verticalLayout.addItem(spacer_item1)

		self.horizontalLayout = QHBoxLayout()

		self.pushButton = QPushButton(tr("Exit"), self.centralwidget)
		self.pushButton.setCursor(Qt.PointingHandCursor)
		self.pushButton.clicked.connect(self.close)
		self.horizontalLayout.addWidget(self.pushButton)

		self.radioButton = QRadioButton(tr("Rock"), self.centralwidget)
		self.radioButton.setCursor(Qt.PointingHandCursor)
		self.radioButton.setToolTip(tr("Rock"))
		self.radioButton.clicked.connect(lambda: self.assignplayermove(Moves.Rock))
		self.horizontalLayout.addWidget(self.radioButton)

		self.radioButton_2 = QRadioButton(tr("Paper"), self.centralwidget)
		self.radioButton_2.setCursor(Qt.PointingHandCursor)
		self.radioButton_2.setToolTip(tr("Paper"))
		self.radioButton_2.clicked.connect(lambda: self.assignplayermove(Moves.Paper))
		self.horizontalLayout.addWidget(self.radioButton_2)

		self.radioButton_3 = QRadioButton(tr("Scissors"), self.centralwidget)
		self.radioButton_3.setCursor(Qt.PointingHandCursor)
		self.radioButton_3.setToolTip(tr("Scissors"))
		self.radioButton_3.clicked.connect(lambda: self.assignplayermove(Moves.Scissors))
		self.horizontalLayout.addWidget(self.radioButton_3)

		self.pushButton_2 = QPushButton(tr("Start Round"), self.centralwidget)
		self.pushButton_2.setCursor(Qt.PointingHandCursor)
		self.pushButton_2.clicked.connect(self.playgame)
		self.horizontalLayout.addWidget(self.pushButton_2)

		x = (self.radioButton, self.radioButton_2, self.radioButton_3)
		random.choice(x).click()

		self.verticalLayout.addLayout(self.horizontalLayout)

		self.statusbar = QStatusBar(self)
		self.zfg = QLabel(
			tr(f"Round 0 (total: {self.settings.value('total_rounds')})  "),
			self.statusbar
		)
		self.gfz = QLabel(
			tr(f" Wins: 0 (total: {self.settings.value('total_wins')}), "
			   f"Losses: 0 (total: {self.settings.value('total_losses')}), "
			   f"Draws: 0 (total: {self.settings.value('total_draws')})  "
			   ),
			self.statusbar
		)
		self.hi = QLabel(
			tr(f" Playtime: 0:00:00 (total: {self.convert(self.settings.value('total_play_time'))})  ") ,
			self.statusbar
		)

		self.statusbar.addPermanentWidget(self.zfg)
		self.statusbar.addPermanentWidget(self.gfz)
		self.statusbar.addPermanentWidget(self.hi)
		self.setStatusBar(self.statusbar)

		temp = QTimer(self)
		temp.timeout.connect(
			lambda: self.zfg.setText(
				tr(
					f"Round {self.rounds_played} (total: {self.settings.value('total_rounds')})  "
				)
			)
		)
		temp.timeout.connect(
			lambda: self.gfz.setText(
				tr(
					f" Wins: {self.wins} (total: {self.settings.value('total_wins')}), "
					f"Losses: {self.losses} (total: {self.settings.value('total_losses')}), "
					f"Draws: {self.draws} (total: {self.settings.value('total_draws')})  "
				)
			)
		)
		temp.timeout.connect(
			lambda: self.hi.setText(
				tr(
					f" Playtime: {self.convert(self.playtime)} "
					f"(total: {self.convert(self.settings.value('total_play_time'))})  "
				)
			)
		)

		temp.start(1000)

		self.setCentralWidget(self.centralwidget)
		self.show()

	def increment(self):
		self.playtime += 1

	@staticmethod
	def convert(seconds: int):
		if seconds == 0:
			return "0:00:00"

		_min, sec = divmod(seconds, 60)
		hour, _min = divmod(_min, 60)
		return "%d:%02d:%02d" % (hour, _min, sec)

	def assignplayermove(self, move: Moves):
		self.playermove = move
		logger.debug(f"Player move changed to %s" % move)

	def closeEvent(self, event: QCloseEvent) -> None:
		self.settings.setValue("last_geometry", self.geometry())

		logger.info("Application exited successfully")

	def rotation(self):
		words = ("Rock...", "Paper...", "Scissors...", "SHOOT!")
		count = 0
		timer = QTimer(self)
		timer.setTimerType(Qt.PreciseTimer)

		def rotate():
			nonlocal words, count, timer

			if count > 2:  # stop after 4 timeouts
				timer.stop()
				timer.deleteLater()
				timer.timeout.disconnect()

			self.newsfeed.setText(self.tr(words[count]))

			logger.debug(f"{count} {words[count]}")

			count += 1

		timer.timeout.connect(rotate)
		timer.start(1000)

	def displayIMG(self):
		self.scene.clear()
		self.scene.update()

		move = random.choice(a := (Moves.Rock, Moves.Paper, Moves.Scissors))
		self.opponentmove = move

		if move == a[0]:
			self.scene.addPixmap(img := self.rock)
		elif move == a[1]:
			self.scene.addPixmap(img := self.paper)
		else:
			self.scene.addPixmap(img := self.scissors)

		w, h = (img.size().width(), img.size().height()) or img.size().toTuple()

		self.graphicsView.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
		self.graphicsView.setVerticalScrollBar(None)
		self.scene.update()

	def determinewinner(self):
		if play(self.opponentmove, self.playermove) == Outcomes.Win:
			self.newsfeed.setText("You Won!")
		elif play(self.opponentmove, self.playermove) == Outcomes.Lose:
			self.newsfeed.setText("You Lost!")
		else:
			self.newsfeed.setText("Draw!")

		logger.log(1, f"Player reached outcome {play(self.opponentmove, self.playermove)}. Bot played {self.opponentmove.name}. Player played {self.playermove.name}")

		return play(self.opponentmove, self.playermove)

	def playgame(self):
		self.rounds_played += 1
		self.settings.setValue("total_rounds", self.settings.value("total_rounds") + 1)

		if self.pushButton_2.text() != "Next Round":
			self.pushButton_2.setText("Next Round")

		self.pushButton_2.setDisabled(True)
		self.rotation()
		a = QTimer(self)
		a.setSingleShot(True)

		def play():
			self.displayIMG()
			out = self.determinewinner()
			self.pushButton_2.setEnabled(True)

			if out == Outcomes.Win:
				self.settings.setValue("total_wins", self.settings.value("total_wins") + 1)
				self.wins += 1
			elif out == Outcomes.Lose:
				self.settings.setValue("total_losses", self.settings.value("total_losses") + 1)
				self.losses += 1
			else:
				self.settings.setValue("total_draws", self.settings.value("total_draws") + 1)
				self.draws += 1

		a.timeout.connect(play)
		a.start(5000)


if __name__ == "__main__":
	application = QApplication(sys.argv)
	application.setWindowIcon(QIcon(":/icons/rps"))

	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("nonimportant.rps.0.0.0")
	
	logger.info("Application started successfully")
	
	window = UIMainWindow()
	sys.exit(application.exec())
