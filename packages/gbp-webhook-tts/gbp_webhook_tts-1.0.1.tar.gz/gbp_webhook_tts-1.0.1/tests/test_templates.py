# pylint: disable=missing-docstring
from unittest import TestCase

from gbp_webhook_tts import templates


class LoadTemplateTests(TestCase):
    def test(self) -> None:
        template = templates.load_template("build_pulled.ssml")

        self.assertEqual("build_pulled.ssml", template.name)
        assert template.filename
        self.assertTrue(template.filename.endswith("/build_pulled.ssml"))

    def test_not_found(self) -> None:
        with self.assertRaises(templates.TemplateNotFoundError):
            templates.load_template("bogus")


class RenderTemplateTests(TestCase):
    def test(self) -> None:
        context = {"machine": "babette", "delay": 0.8}
        template = templates.load_template("build_pulled.ssml")

        text = templates.render_template(template, context)

        expected = """\
<speak>
  <break time="0.8s"/>
  babette
</speak>"""
        self.assertEqual(expected, text)
