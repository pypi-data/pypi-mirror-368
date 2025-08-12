from typing import Iterable, Iterator, Optional

from ._runtime import ensure_loaded
from .types import EnumGroupType, EnumLanguage, EnumMediaType, EnumResolution, EnumSubtitleType, ParseResult


class AniParser :
    """
    轻量包装 .NET 的 Banned.AniParser，提供 parse / parse_batch 方法。
    """

    # 缓存 .NET 类型，避免重复 import 成本
    _AniParser = None
    _ParserOptions = None
    _EnumChineseGlobalization = None
    _Action = None

    @classmethod
    def _load_dotnet_types(cls) :
        if cls._AniParser is None :
            ensure_loaded()
            from Banned.AniParser import AniParser as _AniParser, ParserOptions as _ParserOptions
            from Banned.AniParser.Models.Enums import EnumChineseGlobalization as _ECG
            from System import Action as _Action
            cls._AniParser = _AniParser
            cls._ParserOptions = _ParserOptions
            cls._EnumChineseGlobalization = _ECG
            cls._Action = _Action

    def __init__(self, globalization: str = "NotChange") :
        """
        :param globalization: "Simplified" / "Traditional" / "NotChange"
        """
        self._load_dotnet_types()
        self._mapping = {
            "Simplified"  : self._EnumChineseGlobalization.Simplified,
            "Traditional" : self._EnumChineseGlobalization.Traditional,
            "NotChange"   : self._EnumChineseGlobalization.NotChange,
        }
        if globalization not in self._mapping :
            raise ValueError(f"Unsupported globalization: {globalization}")

        def _cfg(opts) :
            opts.Globalization = self._mapping[globalization]

        # 以配置函数构造 .NET AniParser
        self._parser = self._AniParser(self._Action[self._ParserOptions](_cfg))

    @staticmethod
    def _convert(r) -> ParseResult :
        import System
        return ParseResult(
                title = r.Title,
                episode = (System.Convert.ToDouble(r.Episode) if r.Episode is not None else None),
                version = int(r.Version),
                start_episode = int(r.StartEpisode) if r.StartEpisode is not None else None,
                end_episode = int(r.EndEpisode) if r.EndEpisode is not None else None,
                group = r.Group,
                group_type = EnumGroupType(r.GroupType.GetHashCode()),
                language = EnumLanguage(r.Language.GetHashCode()),
                subtitle_type = EnumSubtitleType(r.SubtitleType.GetHashCode()),
                resolution = EnumResolution(r.Resolution.GetHashCode()),
                source = r.Source,
                web_source = r.WebSource,
                media_type = EnumMediaType(r.MediaType.GetHashCode()),
        )

    def parse(self, title: str) -> Optional[ParseResult] :
        r = self._parser.Parse(title)
        return self._convert(r) if r is not None else None

    def parse_batch(self, titles: Iterable[str]) -> Iterator[ParseResult] :
        from System import Array, String
        arr = Array[String](list(titles))
        for r in self._parser.ParseBatch(arr) :
            yield self._convert(r)

    def get_translation_parser_list(self) -> list[str] :
        """返回按字典序排序后的字幕组名称列表（来自 .NET AniParser.GetTranslationParserList）。"""
        return [str(s) for s in self._parser.GetTranslationParserList()]
