from manim import *
from manim_slides import Slide

from manim_presentations import ModularSlide


class Chapter(ModularSlide):
	def __init__(self, ctx=None, chapter_nb=1, chapter_title="Chapter", chapter_short_title="Chapter"):
		if ctx:
			# update self so that methods of the parent Presentation class have priority
			self.ctx = ctx
		else:
			self.ctx = self
			self.inner_canvas = Group()

		super().__init__(self.ctx)

		self.scenes = []
		self.chapter_nb = chapter_nb
		self.chapter_title = chapter_title
		self.chapter_short_title = chapter_short_title

	def setup(self):
		pass

	def construct(self):
		ctx = self.ctx

		ctx.add(ctx.inner_canvas)

		for i, scene in enumerate(self.scenes):
			scene.setup(ctx)
			scene.construct(ctx)
			if i < len(self.scenes) - 1:
				ctx.next_slide()
				scene.tear_down(ctx)

	def tear_down(self):
		# By default, clear the canvas after the chapter is done
		self.ctx.inner_canvas.remove(*self.ctx.inner_canvas.submobjects)
