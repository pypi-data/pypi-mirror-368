"""
游戏指标查询工具
"""

import logging

from ..models import ErrorCodes, ToolResponse

logger = logging.getLogger(__name__)


class GameIndicatorQueryTool:
    """游戏指标查询工具类"""

    def __init__(self, indicator_manager, config):
        """初始化游戏指标查询工具"""
        self.indicator_manager = indicator_manager
        self.config = config
        self.logger = logger

    def register(self, mcp_server):
        """注册MCP工具"""

        @mcp_server.tool("get_game_available_indicators")
        async def get_game_available_indicators(
            app_id: str, query_type: str = "ad_query"
        ):
            """
            获取指定游戏的可用指标列表

            Args:
                app_id: 游戏ID，可选值：59(正统三国)、61(银河战舰)、48(开心十三张)、78(哈局成语大师)
                query_type: 查询类型，可选值：ad_query(广告数据查询)、material_query(素材数据查询)，默认ad_query

            Returns:
                指定游戏和查询类型的可用指标列表
            """
            try:
                # 验证app_id
                if app_id not in self.config.SUPPORTED_APPIDS:
                    return ToolResponse.error_response(
                        error_code=ErrorCodes.INVALID_PARAMETER,
                        error_message=f"不支持的游戏ID: {app_id}，支持的游戏ID: {list(self.config.SUPPORTED_APPIDS.keys())}",
                    )

                # 验证query_type
                if query_type not in ["ad_query", "material_query"]:
                    return ToolResponse.error_response(
                        error_code=ErrorCodes.INVALID_PARAMETER,
                        error_message=f"不支持的查询类型: {query_type}，支持的类型: ['ad_query', 'material_query']",
                    )

                # 获取游戏信息
                game_info = self.indicator_manager.get_game_info(app_id)
                if not game_info:
                    return ToolResponse.error_response(
                        error_code=ErrorCodes.DATA_NOT_FOUND,
                        error_message=f"未找到游戏 {app_id} 的指标配置",
                    )

                # 根据查询类型获取可用指标
                if query_type == "ad_query":
                    available_indicators = (
                        self.indicator_manager.get_game_available_indicators_for_ad(
                            app_id
                        )
                    )
                else:  # material_query
                    available_indicators = self.indicator_manager.get_game_available_indicators_for_material(
                        app_id
                    )

                game_name = self.config.SUPPORTED_APPIDS.get(app_id, f"游戏{app_id}")

                return ToolResponse.success_response(
                    data={
                        "app_id": app_id,
                        "game_name": game_name,
                        "query_type": query_type,
                        "available_indicators": available_indicators,
                        "indicator_count": len(available_indicators),
                    },
                    record_count=len(available_indicators),
                )

            except Exception as e:
                self.logger.error(f"获取游戏可用指标失败: {e}")
                return ToolResponse.error_response(
                    error_code=ErrorCodes.INTERNAL_ERROR,
                    error_message=f"获取游戏可用指标失败: {str(e)}",
                )

        @mcp_server.tool("get_all_games_indicators")
        async def get_all_games_indicators():
            """
            获取所有游戏的可用指标配置

            Returns:
                所有游戏的可用指标配置
            """
            try:
                all_games = self.indicator_manager.get_all_games()

                games_info = []
                for app_id, game_data in all_games.items():
                    game_name = self.config.SUPPORTED_APPIDS.get(app_id, f"游戏{app_id}")

                    # 获取不同查询类型的指标
                    apis_config = game_data.get("apis", {})
                    ad_indicators = apis_config.get("GetAdCountList", {}).get(
                        "available_indicators", []
                    )
                    material_indicators = apis_config.get(
                        "GetMaterialCountList", {}
                    ).get("available_indicators", [])

                    games_info.append(
                        {
                            "app_id": app_id,
                            "game_name": game_name,
                            "ad_query_indicators": {
                                "available_indicators": ad_indicators,
                                "indicator_count": len(ad_indicators),
                            },
                            "material_query_indicators": {
                                "available_indicators": material_indicators,
                                "indicator_count": len(material_indicators),
                            },
                        }
                    )

                return ToolResponse.success_response(
                    data={"games": games_info, "total_games": len(games_info)},
                    record_count=len(games_info),
                )

            except Exception as e:
                self.logger.error(f"获取所有游戏指标配置失败: {e}")
                return ToolResponse.error_response(
                    error_code=ErrorCodes.INTERNAL_ERROR,
                    error_message=f"获取所有游戏指标配置失败: {str(e)}",
                )

        @mcp_server.tool("validate_indicators_for_game")
        async def validate_indicators_for_game(
            indicators: list[str], app_id: str, query_type: str = "ad_query"
        ):
            """
            验证指定游戏的指标列表

            Args:
                indicators: 要验证的指标列表
                app_id: 游戏ID，可选值：59(正统三国)、61(银河战舰)、48(开心十三张)、78(哈局成语大师)
                query_type: 查询类型，可选值：ad_query(广告数据查询)、material_query(素材数据查询)，默认ad_query

            Returns:
                验证结果，包含有效指标和无效指标列表
            """
            try:
                # 验证app_id
                if app_id not in self.config.SUPPORTED_APPIDS:
                    return ToolResponse.error_response(
                        error_code=ErrorCodes.INVALID_PARAMETER,
                        error_message=f"不支持的游戏ID: {app_id}，支持的游戏ID: {list(self.config.SUPPORTED_APPIDS.keys())}",
                    )

                # 验证query_type
                if query_type not in ["ad_query", "material_query"]:
                    return ToolResponse.error_response(
                        error_code=ErrorCodes.INVALID_PARAMETER,
                        error_message=f"不支持的查询类型: {query_type}，支持的类型: ['ad_query', 'material_query']",
                    )

                # 根据查询类型验证指标
                if query_type == "ad_query":
                    (
                        valid_indicators,
                        invalid_indicators,
                    ) = self.indicator_manager.validate_indicators_for_ad_query(
                        indicators, app_id
                    )
                else:  # material_query
                    (
                        valid_indicators,
                        invalid_indicators,
                    ) = self.indicator_manager.validate_indicators_for_material_query(
                        indicators, app_id
                    )

                game_name = self.config.SUPPORTED_APPIDS.get(app_id, f"游戏{app_id}")

                return ToolResponse.success_response(
                    data={
                        "app_id": app_id,
                        "game_name": game_name,
                        "query_type": query_type,
                        "valid_indicators": valid_indicators,
                        "invalid_indicators": invalid_indicators,
                        "total_indicators": len(indicators),
                        "valid_count": len(valid_indicators),
                        "invalid_count": len(invalid_indicators),
                    },
                    record_count=len(indicators),
                )

            except Exception as e:
                self.logger.error(f"验证游戏指标失败: {e}")
                return ToolResponse.error_response(
                    error_code=ErrorCodes.INTERNAL_ERROR,
                    error_message=f"验证游戏指标失败: {str(e)}",
                )

        @mcp_server.tool("recommend_indicators_by_game_scenario")
        async def recommend_indicators_by_game_scenario(
            scenario: str, app_id: str, query_type: str = "ad_query"
        ):
            """
            基于游戏和业务场景推荐指标

            Args:
                scenario: 业务场景，可选值：投放启动、效果监控、短期评估、深度分析、数据对账、风险预警、财务核算
                app_id: 游戏ID，可选值：59(正统三国)、61(银河战舰)、48(开心十三张)、78(哈局成语大师)
                query_type: 查询类型，可选值：ad_query(广告数据查询)、material_query(素材数据查询)，默认ad_query

            Returns:
                基于游戏和场景的推荐指标列表
            """
            try:
                # 验证app_id
                if app_id not in self.config.SUPPORTED_APPIDS:
                    return ToolResponse.error_response(
                        error_code=ErrorCodes.INVALID_PARAMETER,
                        error_message=f"不支持的游戏ID: {app_id}，支持的游戏ID: {list(self.config.SUPPORTED_APPIDS.keys())}",
                    )

                # 验证场景
                if scenario not in self.config.SCENARIO_MAPPING:
                    return ToolResponse.error_response(
                        error_code=ErrorCodes.INVALID_PARAMETER,
                        error_message=f"不支持的业务场景: {scenario}，支持的场景: {list(self.config.SCENARIO_MAPPING.keys())}",
                    )

                # 验证query_type
                if query_type not in ["ad_query", "material_query"]:
                    return ToolResponse.error_response(
                        error_code=ErrorCodes.INVALID_PARAMETER,
                        error_message=f"不支持的查询类型: {query_type}，支持的类型: ['ad_query', 'material_query']",
                    )

                # 根据查询类型获取推荐指标
                if query_type == "ad_query":
                    recommended_indicators = self.indicator_manager.recommend_indicators_for_ad_query_by_game_scenario(
                        scenario, app_id
                    )
                else:  # material_query
                    recommended_indicators = self.indicator_manager.recommend_indicators_for_material_query_by_game_scenario(
                        scenario, app_id
                    )

                game_name = self.config.SUPPORTED_APPIDS.get(app_id, f"游戏{app_id}")

                return ToolResponse.success_response(
                    data={
                        "app_id": app_id,
                        "game_name": game_name,
                        "query_type": query_type,
                        "scenario": scenario,
                        "recommended_indicators": recommended_indicators,
                        "indicator_count": len(recommended_indicators),
                    },
                    record_count=len(recommended_indicators),
                )

            except Exception as e:
                self.logger.error(f"基于游戏和场景推荐指标失败: {e}")
                return ToolResponse.error_response(
                    error_code=ErrorCodes.INTERNAL_ERROR,
                    error_message=f"基于游戏和场景推荐指标失败: {str(e)}",
                )
