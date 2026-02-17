/**
 * 论坛数据分析平台 - 前端JavaScript
 * 负责数据获取、图表渲染和交互处理
 */

// 初始化统计数据
async function initStats() {
    try {
        const response = await fetch('/api/overview');
        const data = await response.json();
        
        // 更新统计卡片数据
        document.getElementById('total-users').textContent = data.total_users;
        document.getElementById('total-posts').textContent = data.total_posts;
        document.getElementById('total-comments').textContent = data.total_comments;
        document.getElementById('avg-comments-per-post').textContent = data.avg_comments_per_post.toFixed(2);
        
        // 添加数据更新动画
        animateStats();
    } catch (error) {
        console.error('获取概览数据失败:', error);
        showError('无法加载统计数据，请稍后再试。');
    }
}

// 初始化月度发帖趋势图
async function initMonthlyPostsChart() {
    try {
        const response = await fetch('/api/monthly-posts');
        const data = await response.json();
        
        // 处理数据
        const months = data.map(item => item.month);
        const postCounts = data.map(item => item.post_count);
        
        // 初始化图表
        const chartDom = document.getElementById('monthly-posts-chart');
        const myChart = echarts.init(chartDom);
        
        const option = {
            title: {
                text: '月度发帖趋势',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis',
                formatter: '{b}: {c} 篇'
            },
            xAxis: {
                type: 'category',
                data: months,
                axisLabel: {
                    rotate: 45
                }
            },
            yAxis: {
                type: 'value',
                name: '发帖数'
            },
            series: [{
                data: postCounts,
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 8,
                lineStyle: {
                    width: 3,
                    color: '#007bff'
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(0, 123, 255, 0.3)' },
                        { offset: 1, color: 'rgba(0, 123, 255, 0.05)' }
                    ])
                },
                emphasis: {
                    focus: 'series'
                }
            }]
        };
        
        myChart.setOption(option);
        
        // 响应式处理
        window.addEventListener('resize', function() {
            myChart.resize();
        });
    } catch (error) {
        console.error('获取月度发帖数据失败:', error);
        showError('无法加载月度发帖趋势图，请稍后再试。');
    }
}

// 初始化帖子分类分布饼图
async function initCategoryDistributionChart() {
    try {
        const response = await fetch('/api/category-distribution');
        const data = await response.json();
        
        // 初始化图表
        const chartDom = document.getElementById('category-distribution-chart');
        const myChart = echarts.init(chartDom);
        
        const option = {
            title: {
                text: '帖子分类分布',
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c} ({d}%)'
            },
            legend: {
                orient: 'vertical',
                left: 'left'
            },
            series: [{
                name: '帖子分类',
                type: 'pie',
                radius: '60%',
                center: ['50%', '60%'],
                data: data,
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                label: {
                    formatter: '{b}\n{d}%'
                }
            }]
        };
        
        myChart.setOption(option);
        
        // 响应式处理
        window.addEventListener('resize', function() {
            myChart.resize();
        });
    } catch (error) {
        console.error('获取分类分布数据失败:', error);
        showError('无法加载分类分布图，请稍后再试。');
    }
}

// 初始化核心用户排行图
async function initTopUsersChart() {
    try {
        const response = await fetch('/api/top-users');
        const data = await response.json();
        
        // 处理数据
        const usernames = data.map(item => item.username);
        const userScores = data.map(item => item.score);
        
        // 初始化图表
        const chartDom = document.getElementById('top-users-chart');
        const myChart = echarts.init(chartDom);
        
        const option = {
            title: {
                text: '核心用户排行',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                },
                formatter: '{b}: {c} 分'
            },
            xAxis: {
                type: 'value',
                name: '用户声望分'
            },
            yAxis: {
                type: 'category',
                data: usernames.reverse(),
                axisLabel: {
                    interval: 0,
                    rotate: 0,
                    fontSize: 11
                }
            },
            series: [{
                data: userScores.reverse(),
                type: 'bar',
                showBackground: true,
                backgroundStyle: {
                    color: 'rgba(180, 180, 180, 0.2)'
                },
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                        { offset: 0, color: '#83bff6' },
                        { offset: 0.5, color: '#188df0' },
                        { offset: 1, color: '#188df0' }
                    ])
                },
                emphasis: {
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                            { offset: 0, color: '#2378f7' },
                            { offset: 0.7, color: '#2378f7' },
                            { offset: 1, color: '#83bff6' }
                        ])
                    }
                }
            }]
        };
        
        myChart.setOption(option);
        
        // 响应式处理
        window.addEventListener('resize', function() {
            myChart.resize();
        });
    } catch (error) {
        console.error('获取核心用户数据失败:', error);
        showError('无法加载核心用户排行，请稍后再试。');
    }
}

// 统计数据动画效果
function animateStats() {
    const statElements = document.querySelectorAll('.stat-value');
    statElements.forEach(el => {
        el.classList.add('fade-in');
    });
}

// 显示错误信息
function showError(message) {
    const errorElement = document.createElement('div');
    errorElement.className = 'alert alert-danger alert-dismissible fade show';
    errorElement.role = 'alert';
    errorElement.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(errorElement, container.firstChild);
        
        // 3秒后自动关闭错误提示
        setTimeout(() => {
            errorElement.classList.remove('show');
            errorElement.classList.add('hide');
            setTimeout(() => {
                errorElement.remove();
            }, 500);
        }, 3000);
    }
}

// 页面加载完成后执行初始化
document.addEventListener('DOMContentLoaded', function() {
    // 根据当前页面初始化相应组件
    const path = window.location.pathname;
    
    if (path === '/') {
        // 首页初始化
        initStats();
    } else if (path === '/dashboard') {
        // 仪表盘初始化
        initStats();
        initMonthlyPostsChart();
        initCategoryDistributionChart();
        initTopUsersChart();
    }
    
    // 添加导航栏高亮效果
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === path) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });
    
    // 平滑滚动效果
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth'
                });
            }
        });
    });
});