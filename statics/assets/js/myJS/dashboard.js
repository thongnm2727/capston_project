'use strict';

$(document).ready(function () {
    let select = document.getElementById('campaign_select');
    preload(select);
    select.onchange = function () {
        $.ajax({
            type: "GET",
            url: "/dashboard/".concat(select.options[select.selectedIndex].value),
            success: function (data) {
                load(data)
            },
            error: function (xhr, ajaxOptions, thrownError) {
                if (xhr.status === 404) {

                }
            }
        })
    }


});

function preload(select) {
    console.log('test');
    $.ajax({
        type: "GET",
        url: "/dashboard/".concat(select.options[select.selectedIndex].value),
        success: function (data) {
            load(data)
        },
        error: function (xhr, ajaxOptions, thrownError) {
            if (xhr.status === 404) {

            }
        }
    })
}


function load(data) {
    var danang_impression = data['city'][0];
    var hochiminh_impression = data['city'][1];
    var hanoi_impression = data['city'][2];
    var total_impression = danang_impression + hochiminh_impression + hanoi_impression;
    var basicDoughnutElem = document.getElementById('basicDoughnut');
    var danang_rate;
    var hochiminh_rate;
    var hanoi_rate;
    var select = document.getElementById('campaign_select');
    document.getElementById('danang_impression').innerHTML = danang_impression;
    if (total_impression === 0) {
        document.getElementById('first_row_dashboard').hidden = true;
        document.getElementById('second_row_dashboard').hidden = true;
        document.getElementById('no_statistic_alert').hidden = false;
        document.getElementById('no_statistic_alert').innerHTML = '"' + select.options[select.selectedIndex].innerHTML + '"' + ' campaign has no statistic yet';
    } else {
        document.getElementById('first_row_dashboard').hidden = false;
        document.getElementById('second_row_dashboard').hidden = false;
        document.getElementById('no_statistic_alert').hidden = true;
        danang_rate = Math.ceil(danang_impression / total_impression * 100);
        hochiminh_rate = Math.ceil(hochiminh_impression / total_impression * 100);
        hanoi_rate = Math.ceil(hanoi_impression / total_impression * 100);
    }
    document.getElementById('danang_rate').innerHTML = danang_rate.toString().concat('%');
    document.getElementById('danang_progressbar').style.width = danang_rate.toString().concat('%');
    document.getElementById('hochiminh_impression').innerHTML = hochiminh_impression;
    document.getElementById('hochiminh_rate').innerHTML = hochiminh_rate.toString().concat('%');
    document.getElementById('hochiminh_progressbar').style.width = hochiminh_rate.toString().concat('%');
    document.getElementById('hanoi_impression').innerHTML = hanoi_impression;
    document.getElementById('hanoi_rate').innerHTML = hanoi_rate.toString().concat('%');
    document.getElementById('hanoi_progressbar').style.width = hanoi_rate.toString().concat('%');

    if (basicDoughnutElem) {
        var basicDoughnut = echarts.init(basicDoughnutElem);
        basicDoughnut.setOption({

            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            color: ['#ff5721', '#5f6cc1'],
            tooltip: {
                show: false,
                trigger: 'item',
                formatter: "{a} <br/>{b}: {c} ({d}%)"
            },
            xAxis: [{

                axisLine: {
                    show: false
                },
                splitLine: {
                    show: false
                }
            }],
            yAxis: [{

                axisLine: {
                    show: false
                },
                splitLine: {
                    show: false
                }
            }],

            series: [{
                name: 'Sessions',
                type: 'pie',
                radius: ['70%', '85%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: false,
                hoverOffset: 5,
                label: {
                    normal: {
                        show: false,
                        position: 'center',
                        textStyle: {
                            fontSize: '13',
                            fontWeight: 'normal'
                        },
                        formatter: "{a}"
                    },
                    emphasis: {
                        show: true,
                        textStyle: {
                            fontSize: '15',
                            fontWeight: 'bold'
                        },
                        formatter: "{b} \n{c} ({d}%)"
                    }
                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                data: [{value: data['spent_amount'], name: 'Money spend'}, {value: data['money_left'], name: 'Money left'}],
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]

        });
        $(window).on('resize', function () {
            setTimeout(function () {
                basicDoughnut.resize();
            }, 500);
        });
    }

    // STACKED POINTER
    var stackedPointerAreaElem = document.getElementById('stackedPointerArea');
    if (stackedPointerAreaElem) {
        var stackedPointerArea = echarts.init(stackedPointerAreaElem);
        var impression_max = Math.max.apply(Math, data['impressions']);
        var impression_yasis_max = (Number(String(impression_max).charAt(0)) + 1) * (Math.pow(10, String(impression_max).length - 1));
        stackedPointerArea.setOption({
            tooltip: {
                trigger: 'axis',

                axisPointer: {
                    animation: true
                }
            },
            grid: {
                left: '8%',
                top: '4%',
                right: '7%',
                bottom: '10%'
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: data['days'],
                axisLabel: {
                    formatter: '{value}',
                    color: '#666',
                    fontSize: 12,
                    fontStyle: 'normal',
                    fontWeight: 400

                },
                axisLine: {
                    lineStyle: {
                        color: '#ccc',
                        width: 1
                    }
                },
                axisTick: {
                    lineStyle: {
                        color: '#ccc',
                        width: 1
                    }
                },
                splitLine: {
                    show: false,
                    lineStyle: {
                        color: '#ccc',
                        width: 1
                    }
                }
            },
            yAxis: {
                type: 'value',
                min: 0,
                max: impression_yasis_max,
                interval: impression_yasis_max / 5,
                axisLabel: {
                    formatter: '{value}',
                    color: '#666',
                    fontSize: 12,
                    fontStyle: 'normal',
                    fontWeight: 400

                },
                axisLine: {
                    lineStyle: {
                        color: '#ccc',
                        width: 1
                    }
                },
                axisTick: {
                    lineStyle: {
                        color: '#ccc',
                        width: 1
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: '#ddd',
                        width: 1,
                        opacity: 0.5
                    }
                }
            },
            series: [{
                name: 'Impression',
                type: 'line',
                smooth: true,
                data: data['impressions'],
                symbolSize: 8,
                lineStyle: {
                    color: 'rgb(255, 87, 33)',
                    opacity: 1,
                    width: 1.5
                },
                itemStyle: {
                    color: '#ff5721',
                    borderColor: '#ff5721',
                    borderWidth: 1.5
                },
                areaStyle: {
                    normal: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [{
                                offset: 0,
                                color: 'rgba(255, 87, 33, 1)'
                            }, {
                                offset: 0.3,
                                color: 'rgba(255, 87, 33, 0.7)'
                            }, {
                                offset: 1,
                                color: 'rgba(255, 87, 33, 0)'
                            }]
                        }
                    }
                }
            }, {
                name: 'Clicks',
                type: 'line',
                smooth: true,
                data: data['clicks'],
                symbolSize: 8,
                lineStyle: {
                    color: 'rgb(95, 107, 194)',
                    opacity: 1,
                    width: 1.5
                },
                itemStyle: {
                    color: '#5f6cc1',
                    borderColor: '#5f6cc1',
                    borderWidth: 1.5
                },
                areaStyle: {
                    normal: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [{
                                offset: 0,
                                color: 'rgba(95, 107, 194, 1)'
                            }, {
                                offset: 0.5,
                                color: 'rgba(95, 107, 194, 0.7)'
                            }, {
                                offset: 1,
                                color: 'rgba(95, 107, 194, 0)'
                            }]
                        }
                    }
                }
            }]
        });
        $(window).on('resize', function () {
            setTimeout(function () {
                stackedPointerArea.resize();
            }, 500);
        });
    }

    var basicLineElem = document.getElementById('basicLine');
    if (basicLineElem) {
        var basicLine = echarts.init(basicLineElem);
        basicLine.setOption({
            tooltip: {
                show: true,
                trigger: 'axis',
                axisPointer: {
                    type: 'line',
                    animation: true
                }
            },
            grid: {
                top: '10%',
                left: '80',
                right: '40',
                bottom: '40'
            },
            xAxis: {
                type: 'category',
                data: data['days'],
                axisLine: {
                    show: false
                },
                axisLabel: {
                    show: true
                },
                axisTick: {
                    show: false
                }
            },
            yAxis: {
                type: 'value',
                axisLine: {
                    show: false
                },
                axisLabel: {
                    show: true
                },
                axisTick: {
                    show: false
                },
                splitLine: {
                    show: true
                }
            },
            series: [{
                data: data['money_spend_inweek'],
                type: 'line',
                showSymbol: true,
                smooth: true,
                color: '#639',
                lineStyle: {
                    opacity: 1,
                    width: 2
                }
            }]
        });
        $(window).on('resize', function () {
            setTimeout(function () {
                basicLine.resize();
            }, 500);
        });
    }

    let stackedPieElem = document.getElementById('stackedPie');
    if (stackedPieElem) {
        let stackedPie = echarts.init(stackedPieElem);
        stackedPie.setOption({
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            color: ['#639', '#63845', '#ebcb37', '#a1b968', '#0d94bc', '#135bba'],

            tooltip: {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },

            visualMap: {
                show: false,
                min: 80,
                max: 100000000,
                inRange: {
                    colorLightness: [0, 50]
                }
            },
            series: [{
                name: 'Source',
                type: 'pie',
                radius: '85%',
                center: ['50%', '50%'],
                data: [{
                    value: 645890,
                    name: 'Impression'
                },
                    {
                        value: 389281,
                        name: 'Click'
                    }
                ].sort(function (a, b) {
                    return a.value - b.value;
                }),
                roseType: 'radius',
                label: {
                    normal: {
                        textStyle: {
                            color: '#333'
                        }
                    }
                },
                labelLine: {
                    normal: {
                        lineStyle: {
                            color: '#333'
                        },
                        smooth: 0.2,
                        length: 10,
                        length2: 20
                    }
                },
                itemStyle: {
                    normal: {
                        color: 'rgb(102, 51, 153)',
                        shadowBlur: 200,
                        shadowColor: 'rgba(0, 0, 0, 0.0)'
                    }
                },

                animationType: 'scale',
                animationEasing: 'elasticOut',
                animationDelay: function (idx) {
                    return Math.random() * 200;
                }
            }]
        });
        $(window).on('resize', function () {
            setTimeout(() => {
                stackedPie.resize();
            }, 500);
        });
    }

    // Chart in Dashboard version 1


    // dummy charts

    // let dummyChartElem = document.getElementById('dummyChart');
    // if (dummyChartElem) {
    //     let dummyChart = echarts.init(dummyChartElem);


    //     dummyChart.setOption({
    //         grid: {
    //             left: '3%',
    //             right: '4%',
    //             bottom: '3%',
    //             containLabel: true
    //         },


    //     });
    //     $(window).on('resize', function() {
    //         setTimeout(() => {
    //             dummyChart.resize();
    //         }, 500);
    //     });
    // }

}