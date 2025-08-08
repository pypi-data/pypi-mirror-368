"""
路由监控管理界面
提供完整的监控数据查看和管理功能的Flask路由

主要功能：
1. 实时监控面板
2. 统计数据查看
3. 告警信息展示
4. 报告生成
5. 数据清理管理

"""

from flask import Blueprint, jsonify, request, render_template_string
from datetime import datetime, timedelta
from mdbq.route.monitor import route_monitor, monitor_request, get_request_id
from mdbq.route.analytics import (
    get_realtime_metrics, get_traffic_trend, get_endpoint_analysis,
    get_user_behavior_analysis, get_performance_alerts, generate_daily_report
)
import json

# 创建监控管理蓝图
monitor_bp = Blueprint('monitor', __name__, url_prefix='/admin/monitor')


@monitor_bp.route('/dashboard', methods=['GET'])
@monitor_request
def dashboard():
    """监控面板首页"""
    try:
        # 获取实时指标
        realtime_data = get_realtime_metrics()
        
        # 获取告警信息
        alerts = get_performance_alerts()
        
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': {
                'realtime_metrics': realtime_data,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get dashboard data',
            'error': str(e)
        }), 500


@monitor_bp.route('/metrics/realtime', methods=['GET'])
@monitor_request
def realtime_metrics():
    """获取实时监控指标"""
    try:
        data = get_realtime_metrics()
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get realtime metrics',
            'error': str(e)
        }), 500


@monitor_bp.route('/traffic/trend', methods=['GET'])
@monitor_request
def traffic_trend():
    """获取流量趋势分析"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            days = 7
            
        data = get_traffic_trend(days)
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get traffic trend',
            'error': str(e)
        }), 500


@monitor_bp.route('/endpoints/analysis', methods=['GET'])
@monitor_request
def endpoint_analysis():
    """获取端点性能分析"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            days = 7
            
        data = get_endpoint_analysis(days)
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get endpoint analysis',
            'error': str(e)
        }), 500


@monitor_bp.route('/users/behavior', methods=['GET'])
@monitor_request
def user_behavior():
    """获取用户行为分析"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            days = 7
            
        data = get_user_behavior_analysis(days)
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get user behavior analysis',
            'error': str(e)
        }), 500


@monitor_bp.route('/alerts', methods=['GET'])
@monitor_request
def alerts():
    """获取性能告警信息"""
    try:
        data = get_performance_alerts()
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get alerts',
            'error': str(e)
        }), 500


@monitor_bp.route('/reports/daily', methods=['GET'])
@monitor_request
def daily_report():
    """获取日报告"""
    try:
        date_str = request.args.get('date')
        target_date = None
        
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'code': 400,
                    'status': 'error',
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        data = generate_daily_report(target_date)
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to generate daily report',
            'error': str(e)
        }), 500


@monitor_bp.route('/requests/search', methods=['POST'])
@monitor_request
def search_requests():
    """搜索请求记录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': 'Missing request data'
            }), 400
        
        # 搜索参数
        page = data.get('page', 1)
        page_size = min(data.get('page_size', 50), 200)  # 限制页面大小
        
        filters = data.get('filters', {})
        start_time = filters.get('start_time')
        end_time = filters.get('end_time')
        endpoint = filters.get('endpoint')
        client_ip = filters.get('client_ip')
        method = filters.get('method')
        status_code = filters.get('status_code')
        min_response_time = filters.get('min_response_time')
        
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                # 构建查询条件
                where_conditions = ["1=1"]
                params = []
                
                if start_time:
                    where_conditions.append("timestamp >= %s")
                    params.append(start_time)
                
                if end_time:
                    where_conditions.append("timestamp <= %s")
                    params.append(end_time)
                
                if endpoint:
                    where_conditions.append("endpoint LIKE %s")
                    params.append(f"%{endpoint}%")
                
                if client_ip:
                    where_conditions.append("client_ip = %s")
                    params.append(client_ip)
                
                if method:
                    where_conditions.append("method = %s")
                    params.append(method)
                
                if status_code:
                    where_conditions.append("response_status = %s")
                    params.append(status_code)
                
                if min_response_time:
                    where_conditions.append("process_time >= %s")
                    params.append(min_response_time)
                
                where_clause = " AND ".join(where_conditions)
                
                # 获取总数
                count_sql = f"SELECT COUNT(*) as total FROM api_request_logs WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total_count = cursor.fetchone()['total']
                
                # 分页查询
                offset = (page - 1) * page_size
                search_sql = f"""
                    SELECT 
                        request_id, timestamp, method, endpoint, client_ip, real_ip,
                        response_status, process_time, user_agent, referer,
                        is_bot, is_mobile, browser_name, os_name
                    FROM api_request_logs 
                    WHERE {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT %s OFFSET %s
                """
                
                cursor.execute(search_sql, params + [page_size, offset])
                results = cursor.fetchall()
                
                return jsonify({
                    'code': 0,
                    'status': 'success',
                    'message': 'success',
                    'data': {
                        'requests': results,
                        'pagination': {
                            'current_page': page,
                            'page_size': page_size,
                            'total_count': total_count,
                            'total_pages': (total_count + page_size - 1) // page_size
                        }
                    }
                })
        finally:
            connection.close()
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to search requests',
            'error': str(e)
        }), 500


@monitor_bp.route('/requests/<request_id>', methods=['GET'])
@monitor_request
def get_request_detail(request_id):
    """获取请求详细信息"""
    try:
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM api_request_logs WHERE request_id = %s
                """, (request_id,))
                
                request_detail = cursor.fetchone()
                
                if not request_detail:
                    return jsonify({
                        'code': 404,
                        'status': 'error',
                        'message': 'Request not found'
                    }), 404
                
                # 安全地转换JSON字段
                json_fields = ['request_headers', 'request_params', 'request_body', 'device_info', 'business_data', 'tags']
                for field in json_fields:
                    if request_detail.get(field):
                        try:
                            # 使用json.loads替代eval，更安全
                            if isinstance(request_detail[field], str):
                                request_detail[field] = json.loads(request_detail[field])
                        except (json.JSONDecodeError, TypeError):
                            # 如果解析失败，保持原值
                            pass
                
                return jsonify({
                    'code': 0,
                    'status': 'success',
                    'message': 'success',
                    'data': request_detail
                })
        finally:
            connection.close()
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get request detail',
            'error': str(e)
        }), 500


@monitor_bp.route('/statistics/summary', methods=['GET'])
@monitor_request
def statistics_summary():
    """获取统计摘要"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            days = 7
        
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                
                # 综合统计
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_requests,
                        COUNT(DISTINCT client_ip) as unique_ips,
                        COUNT(DISTINCT endpoint) as unique_endpoints,
                        COUNT(DISTINCT DATE(timestamp)) as active_days,
                        AVG(process_time) as avg_response_time,
                        MAX(process_time) as max_response_time,
                        SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as error_count,
                        SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) / COUNT(*) * 100 as error_rate,
                        SUM(CASE WHEN is_bot = 1 THEN 1 ELSE 0 END) as bot_requests,
                        SUM(CASE WHEN is_mobile = 1 THEN 1 ELSE 0 END) as mobile_requests,
                        SUM(request_size) as total_request_size,
                        SUM(response_size) as total_response_size
                    FROM api_request_logs 
                    WHERE DATE(timestamp) BETWEEN %s AND %s
                """, (start_date, end_date))
                
                summary = cursor.fetchone()
                
                # 每日趋势
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as requests,
                        COUNT(DISTINCT client_ip) as unique_ips,
                        AVG(process_time) as avg_response_time,
                        SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors
                    FROM api_request_logs 
                    WHERE DATE(timestamp) BETWEEN %s AND %s
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """, (start_date, end_date))
                
                daily_trend = cursor.fetchall()
                
                return jsonify({
                    'code': 0,
                    'status': 'success',
                    'message': 'success',
                    'data': {
                        'period': f'{start_date} to {end_date}',
                        'summary': summary,
                        'daily_trend': daily_trend
                    }
                })
        finally:
            connection.close()
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get statistics summary',
            'error': str(e)
        }), 500


@monitor_bp.route('/data/cleanup', methods=['POST'])
@monitor_request  
def data_cleanup():
    """数据清理功能"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': 'Missing request data'
            }), 400
        
        cleanup_type = data.get('type', 'old_logs')
        days_to_keep = data.get('days_to_keep', 30)
        
        if days_to_keep < 7:  # 至少保留7天
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': 'Must keep at least 7 days of data'
            }), 400
        
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                cleanup_date = datetime.now() - timedelta(days=days_to_keep)
                
                if cleanup_type == 'old_logs':
                    # 清理旧的请求日志
                    cursor.execute("""
                        DELETE FROM api_request_logs 
                        WHERE timestamp < %s
                    """, (cleanup_date,))
                    
                    deleted_count = cursor.rowcount
                    
                elif cleanup_type == 'old_statistics':
                    # 清理旧的统计数据
                    cursor.execute("""
                        DELETE FROM api_access_statistics 
                        WHERE date < %s
                    """, (cleanup_date.date(),))
                    
                    deleted_count = cursor.rowcount
                    
                elif cleanup_type == 'old_ip_stats':
                    # 清理旧的IP统计
                    cursor.execute("""
                        DELETE FROM ip_access_statistics 
                        WHERE date < %s
                    """, (cleanup_date.date(),))
                    
                    deleted_count = cursor.rowcount
                    
                else:
                    return jsonify({
                        'code': 400,
                        'status': 'error',
                        'message': 'Invalid cleanup type'
                    }), 400
                
            connection.commit()
            
            return jsonify({
                'code': 0,
                'status': 'success',
                'message': 'Data cleanup completed',
                'data': {
                    'cleanup_type': cleanup_type,
                    'deleted_count': deleted_count,
                    'cleanup_date': cleanup_date.isoformat()
                }
            })
        finally:
            connection.close()
         
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to cleanup data',
            'error': str(e)
        }), 500


@monitor_bp.route('/health', methods=['GET'])
def health_check():
    """监控系统健康检查"""
    try:
        # 检查数据库连接
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "OK"
        
            # 检查最近的数据
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as recent_count 
                    FROM api_request_logs 
                    WHERE timestamp >= %s
                """, (datetime.now() - timedelta(hours=1),))
                
                recent_requests = cursor.fetchone()['recent_count']
        finally:
            connection.close()
        
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'Monitor system is healthy',
            'data': {
                'database_status': db_status,
                'recent_requests_count': recent_requests,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Monitor system health check failed',
            'error': str(e)
        }), 500


# 导出蓝图注册函数
def register_routes(app):
    """注册监控路由到Flask应用"""
    app.register_blueprint(monitor_bp) 