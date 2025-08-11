"""Visual report generation for vibe test results using Plotly with timing analysis."""

from typing import Dict, List, Any
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


class VibeTestReportGenerator:
    """Generates HTML reports with Plotly visualizations for vibe test results including timing analysis."""
    
    def __init__(self, model: str, analysis_model: str):
        """Initialize the report generator.
        
        Args:
            model: The chat model used for testing
            analysis_model: The analysis model used for testing
        """
        self.model = model
        self.analysis_model = analysis_model
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def create_action_success_chart(self, action_name: str, results: Dict) -> str:
        """Create a bar chart showing success rate for each phrase of an action.
        
        Args:
            action_name: Name of the action
            results: Test results for the action
            
        Returns:
            HTML div containing the Plotly chart
        """
        phrases = []
        success_rates = []
        colors = []
        
        for phrase, data in results['phrase_results'].items():
            # Truncate long phrases for display
            display_phrase = phrase[:40] + '...' if len(phrase) > 40 else phrase
            phrases.append(display_phrase)
            success_rates.append(data['success_rate'])
            # Color based on success rate
            if data['success_rate'] >= 80:
                colors.append('green')
            elif data['success_rate'] >= 60:
                colors.append('yellow')
            else:
                colors.append('red')
        
        fig = go.Figure(data=[
            go.Bar(
                x=phrases,
                y=success_rates,
                marker_color=colors,
                text=[f"{rate:.1f}%" for rate in success_rates],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Success Rate: %{y:.1f}%<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=f"{action_name} - Success Rate by Phrase",
            xaxis_title="Test Phrase",
            yaxis_title="Success Rate (%)",
            yaxis_range=[0, 110],
            showlegend=False,
            height=400,
            margin=dict(b=100),
            xaxis_tickangle=-45
        )
        
        # Convert to HTML div
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id=f"success-{action_name.replace(' ', '-')}")
    
    def create_timing_performance_chart(self, action_name: str, results: Dict) -> str:
        """Create a combined chart showing timing performance for each phrase.
        
        Args:
            action_name: Name of the action
            results: Test results for the action
            
        Returns:
            HTML div containing the Plotly chart
        """
        phrases = []
        avg_times = []
        consistency_scores = []
        colors_time = []
        colors_consistency = []
        
        for phrase, data in results['phrase_results'].items():
            display_phrase = phrase[:30] + '...' if len(phrase) > 30 else phrase
            phrases.append(display_phrase)
            
            timing_stats = data['timing_stats']
            avg_times.append(timing_stats['mean'])
            consistency_scores.append(timing_stats['consistency_score'])
            
            # Color coding for average time
            if timing_stats['mean'] < 1.0:
                colors_time.append('green')
            elif timing_stats['mean'] < 3.0:
                colors_time.append('yellow')
            else:
                colors_time.append('red')
            
            # Color coding for consistency
            if timing_stats['consistency_score'] >= 80:
                colors_consistency.append('green')
            elif timing_stats['consistency_score'] >= 60:
                colors_consistency.append('yellow')
            else:
                colors_consistency.append('red')
        
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add average time bars
        fig.add_trace(
            go.Bar(
                name="Average Time",
                x=phrases,
                y=avg_times,
                marker_color=colors_time,
                text=[f"{time:.2f}s" for time in avg_times],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Average Time: %{y:.2f}s<extra></extra>',
                yaxis="y"
            ),
            secondary_y=False,
        )
        
        # Add consistency line
        fig.add_trace(
            go.Scatter(
                name="Consistency Score",
                x=phrases,
                y=consistency_scores,
                mode='lines+markers',
                line=dict(color='purple', width=3),
                marker=dict(size=8, color=colors_consistency, line=dict(color='purple', width=2)),
                text=[f"{score:.1f}" for score in consistency_scores],
                textposition='top center',
                hovertemplate='<b>%{x}</b><br>Consistency: %{y:.1f}/100<extra></extra>',
                yaxis="y2"
            ),
            secondary_y=True,
        )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Test Phrase", tickangle=-45)
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Average Time (seconds)", secondary_y=False)
        fig.update_yaxes(title_text="Consistency Score (0-100)", secondary_y=True, range=[0, 110])
        
        fig.update_layout(
            title=f"{action_name} - Timing Performance Analysis",
            height=500,
            margin=dict(b=100),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False, 
                         div_id=f"timing-{action_name.replace(' ', '-')}")
    
    def create_secondary_actions_chart(self, action_name: str, results: Dict) -> str:
        """Create a grouped bar chart showing secondary actions triggered for each phrase.
        
        Args:
            action_name: Name of the action
            results: Test results for the action
            
        Returns:
            HTML div containing the Plotly chart
        """
        # Collect all unique secondary actions across all phrases
        all_secondary_actions = set()
        for phrase_data in results['phrase_results'].values():
            all_secondary_actions.update(phrase_data['secondary_action_counts'].keys())
        
        if not all_secondary_actions:
            # No secondary actions triggered - create an empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No secondary actions were triggered for any test phrase",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                title=f"{action_name} - Secondary Actions Triggered",
                height=400,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig.to_html(full_html=False, include_plotlyjs=False, 
                             div_id=f"secondary-{action_name.replace(' ', '-')}")
        
        # Prepare data for grouped bar chart
        phrases = []
        traces = []
        
        for phrase, data in results['phrase_results'].items():
            display_phrase = phrase[:30] + '...' if len(phrase) > 30 else phrase
            phrases.append(display_phrase)
        
        # Create a trace for each secondary action
        for secondary_action in sorted(all_secondary_actions):
            counts = []
            for phrase_data in results['phrase_results'].values():
                count = phrase_data['secondary_action_counts'].get(secondary_action, 0)
                total = phrase_data['total']
                # Store as percentage
                percentage = (count / total * 100) if total > 0 else 0
                counts.append(percentage)
            
            traces.append(go.Bar(
                name=secondary_action,
                x=phrases,
                y=counts,
                text=[f"{c:.0f}%" if c > 0 else "" for c in counts],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>' + f'{secondary_action}: ' + '%{y:.1f}%<extra></extra>'
            ))
        
        fig = go.Figure(data=traces)
        
        fig.update_layout(
            title=f"{action_name} - Secondary Actions Triggered by Phrase",
            xaxis_title="Test Phrase",
            yaxis_title="Trigger Rate (%)",
            barmode='group',
            height=500,
            margin=dict(b=100),
            xaxis_tickangle=-45,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False, 
                         div_id=f"secondary-{action_name.replace(' ', '-')}")
    
    def create_overall_summary_chart(self, test_results: Dict) -> str:
        """Create an overall summary chart showing all actions' performance.
        
        Args:
            test_results: All test results
            
        Returns:
            HTML div containing the Plotly chart
        """
        action_names = []
        success_rates = []
        avg_times = []
        colors = []
        
        for action_name, test_data in test_results.items():
            action_names.append(action_name)
            rate = test_data['results']['success_rate']
            avg_time = test_data['results']['overall_timing_stats']['mean']
            success_rates.append(rate)
            avg_times.append(avg_time)
            
            # Color based on pass/fail
            if rate >= 60:
                colors.append('green')
            else:
                colors.append('red')
        
        # Create subplot with secondary y-axis for timing
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add success rate bars
        fig.add_trace(
            go.Bar(
                name="Success Rate",
                x=action_names,
                y=success_rates,
                marker_color=colors,
                text=[f"{rate:.1f}%" for rate in success_rates],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Success Rate: %{y:.1f}%<extra></extra>',
                yaxis="y"
            ),
            secondary_y=False,
        )
        
        # Add average time line
        fig.add_trace(
            go.Scatter(
                name="Average Time",
                x=action_names,
                y=avg_times,
                mode='lines+markers',
                line=dict(color='purple', width=3),
                marker=dict(size=10, color='purple'),
                text=[f"{time:.2f}s" for time in avg_times],
                textposition='top center',
                hovertemplate='<b>%{x}</b><br>Average Time: %{y:.2f}s<extra></extra>',
                yaxis="y2"
            ),
            secondary_y=True,
        )
        
        # Add pass threshold line for success rate
        fig.add_hline(
            y=60, 
            line_dash="dash", 
            line_color="orange",
            annotation_text="Pass Threshold (60%)",
            secondary_y=False
        )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Action", tickangle=-45)
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Success Rate (%)", range=[0, 110], secondary_y=False)
        fig.update_yaxes(title_text="Average Time (seconds)", secondary_y=True)
        
        fig.update_layout(
            title="Overall Vibe Test Results - Success Rate & Performance",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id="overall-summary")
    
    def create_performance_comparison_chart(self, test_results: Dict) -> str:
        """Create a scatter plot comparing consistency vs speed for all actions.
        
        Args:
            test_results: All test results
            
        Returns:
            HTML div containing the Plotly chart
        """
        action_names = []
        avg_times = []
        consistency_scores = []
        success_rates = []
        colors = []
        sizes = []
        
        for action_name, test_data in test_results.items():
            timing_stats = test_data['results']['overall_timing_stats']
            action_names.append(action_name)
            avg_times.append(timing_stats['mean'])
            consistency_scores.append(timing_stats['consistency_score'])
            success_rate = test_data['results']['success_rate']
            success_rates.append(success_rate)
            
            # Color based on success rate
            if success_rate >= 80:
                colors.append('green')
            elif success_rate >= 60:
                colors.append('yellow')
            else:
                colors.append('red')
            
            # Size based on success rate (larger = better)
            sizes.append(max(10, success_rate / 2))
        
        fig = go.Figure(data=go.Scatter(
            x=avg_times,
            y=consistency_scores,
            mode='markers+text',
            marker=dict(
                size=sizes,
                color=colors,
                line=dict(color='black', width=1),
                opacity=0.8
            ),
            text=action_names,
            textposition='top center',
            customdata=success_rates,
            hovertemplate='<b>%{text}</b><br>' +
                         'Average Time: %{x:.2f}s<br>' +
                         'Consistency: %{y:.1f}/100<br>' +
                         'Success Rate: %{customdata:.1f}%' + 
                         '<extra></extra>',
            name=""
        ))
        
        # Add quadrant lines
        fig.add_vline(x=2.0, line_dash="dash", line_color="gray", 
                     annotation_text="2s threshold", annotation_position="top")
        fig.add_hline(y=80, line_dash="dash", line_color="gray",
                     annotation_text="High Consistency (80+)", annotation_position="right")
        
        fig.update_layout(
            title="Performance Comparison: Speed vs Consistency",
            xaxis_title="Average Time (seconds)",
            yaxis_title="Consistency Score (0-100)",
            xaxis=dict(range=[0, max(avg_times) * 1.1]),
            yaxis=dict(range=[0, 105]),
            height=500,
            showlegend=False,
            annotations=[
                dict(
                    text="Fast & Consistent<br>(Ideal)",
                    x=0.5, y=95,
                    showarrow=False,
                    font=dict(size=12, color="green"),
                    bgcolor="rgba(0,255,0,0.1)",
                    bordercolor="green",
                    borderwidth=1
                ),
                dict(
                    text="Slow but Consistent",
                    x=max(avg_times) * 0.8, y=95,
                    showarrow=False,
                    font=dict(size=12, color="orange"),
                    bgcolor="rgba(255,165,0,0.1)",
                    bordercolor="orange",
                    borderwidth=1
                ),
                dict(
                    text="Fast but Inconsistent",
                    x=0.5, y=20,
                    showarrow=False,
                    font=dict(size=12, color="orange"),
                    bgcolor="rgba(255,165,0,0.1)",
                    bordercolor="orange",
                    borderwidth=1
                ),
                dict(
                    text="Slow & Inconsistent<br>(Needs Work)",
                    x=max(avg_times) * 0.8, y=20,
                    showarrow=False,
                    font=dict(size=12, color="red"),
                    bgcolor="rgba(255,0,0,0.1)",
                    bordercolor="red",
                    borderwidth=1
                )
            ]
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id="performance-comparison")
    
    def generate_html_header(self) -> str:
        """Generate the HTML header with styles and scripts.
        
        Returns:
            HTML header string
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibe Test Report - {self.timestamp}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        h1 {{
            color: #333;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .model-info {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .model-info h3 {{
            margin-top: 0;
            color: #495057;
        }}
        .model-detail {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
        }}
        .model-label {{
            font-weight: 600;
            color: #6c757d;
        }}
        .action-section {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}
        .action-header {{
            margin-bottom: 20px;
        }}
        .action-name {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 10px;
        }}
        .action-description {{
            color: #666;
            font-style: italic;
            margin-bottom: 10px;
        }}
        .action-stats {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        .stat-box {{
            background: white;
            padding: 10px 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        .pass {{
            color: #28a745;
        }}
        .fail {{
            color: #dc3545;
        }}
        .chart-container {{
            margin: 20px 0;
        }}
        .summary-section {{
            margin-top: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
        }}
        .summary-title {{
            font-size: 2em;
            margin-bottom: 20px;
            text-align: center;
        }}
        .summary-stats {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            color: #6c757d;
        }}
        .timing-highlight {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Vibe Test Report</h1>
        <div class="subtitle">AI Decision-Making Consistency & Performance Analysis</div>
        <div class="subtitle">Generated: {self.timestamp}</div>
        
        <div class="model-info">
            <h3>Test Configuration</h3>
            <div class="model-detail">
                <span class="model-label">Chat Model:</span>
                <span>{self.model}</span>
            </div>
            <div class="model-detail">
                <span class="model-label">Analysis Model:</span>
                <span>{self.analysis_model}</span>
            </div>
            <div class="model-detail">
                <span class="model-label">Test Mode:</span>
                <span>Multi-action selection with timing analysis</span>
            </div>
        </div>
"""
    
    def generate_action_section(self, action_name: str, test_data: Dict) -> str:
        """Generate HTML for a single action's results.
        
        Args:
            action_name: Name of the action
            test_data: Test data for the action
            
        Returns:
            HTML string for the action section
        """
        results = test_data['results']
        passed = test_data['passed']
        status_icon = "✅" if passed else "❌"
        pass_class = 'pass' if passed else 'fail'
        
        # Get timing stats
        timing_stats = results['overall_timing_stats']
        
        # Generate charts
        success_chart = self.create_action_success_chart(action_name, results)
        timing_chart = self.create_timing_performance_chart(action_name, results)
        secondary_chart = self.create_secondary_actions_chart(action_name, results)
        
        return f"""
        <div class="action-section">
            <div class="action-header">
                <div class="action-name">{action_name} {status_icon}</div>
                <div class="action-description">{results['action_description']}</div>
                <div class="action-stats">
                    <div class="stat-box">
                        <div class="stat-label">Overall Success Rate</div>
                        <div class="stat-value {pass_class}">{results['success_rate']:.1f}%</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Tests Passed</div>
                        <div class="stat-value">{results['total_correct']}/{results['total_tests']}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Average Time</div>
                        <div class="stat-value">{timing_stats['mean']:.2f}s</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Performance</div>
                        <div class="stat-value">{timing_stats['performance_category']}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Consistency</div>
                        <div class="stat-value">{timing_stats['consistency_score']:.1f}/100</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Status</div>
                        <div class="stat-value {pass_class}">{'PASS' if passed else 'FAIL'}</div>
                    </div>
                </div>
                <div class="timing-highlight">
                    <strong>⏱️ Timing Analysis:</strong> 
                    Range: {timing_stats['min']:.2f}s - {timing_stats['max']:.2f}s | 
                    Median: {timing_stats['median']:.2f}s | 
                    95th percentile: {timing_stats['p95']:.2f}s
                </div>
            </div>
            <div class="chart-container">
                {success_chart}
            </div>
            <div class="chart-container">
                {timing_chart}
            </div>
            <div class="chart-container">
                {secondary_chart}
            </div>
        </div>
"""
    
    def generate_summary_section(self, test_results: Dict) -> str:
        """Generate the summary section of the report.
        
        Args:
            test_results: All test results
            
        Returns:
            HTML string for the summary section
        """
        total_actions = len(test_results)
        passed_actions = sum(1 for data in test_results.values() if data['passed'])
        failed_actions = total_actions - passed_actions
        all_passed = passed_actions == total_actions
        
        # Calculate overall timing stats
        all_times = []
        for test_data in test_results.values():
            all_times.extend(test_data['results']['overall_timing_stats']['raw_times'])
        
        if all_times:
            avg_overall_time = sum(all_times) / len(all_times)
            fastest_overall = min(all_times)
            slowest_overall = max(all_times)
        else:
            avg_overall_time = fastest_overall = slowest_overall = 0.0
        
        return f"""
        <div class="summary-section">
            <div class="summary-title">Test Summary</div>
            <div class="summary-stats">
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Total Actions Tested</div>
                    <div class="stat-value">{total_actions}</div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Actions Passed</div>
                    <div class="stat-value pass">{passed_actions}</div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Actions Failed</div>
                    <div class="stat-value fail">{failed_actions}</div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Overall Result</div>
                    <div class="stat-value {'pass' if all_passed else 'fail'}">
                        {'ALL PASS' if all_passed else f'{passed_actions}/{total_actions} PASS'}
                    </div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Average Response Time</div>
                    <div class="stat-value">{avg_overall_time:.2f}s</div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Response Range</div>
                    <div class="stat-value">{fastest_overall:.2f}s - {slowest_overall:.2f}s</div>
                </div>
            </div>
        </div>
"""
    
    def generate_footer(self) -> str:
        """Generate the HTML footer.
        
        Returns:
            HTML footer string
        """
        return f"""
        <div class="footer">
            <p>Report generated by OllamaPy Vibe Test Runner with Timing Analysis</p>
            <p>Models: {self.model} (chat) | {self.analysis_model} (analysis)</p>
            <p>Timing measurements include full action selection pipeline analysis</p>
        </div>
    </div>
</body>
</html>
"""
    
    def generate_full_report(self, test_results: Dict) -> str:
        """Generate the complete HTML report.
        
        Args:
            test_results: All test results
            
        Returns:
            Complete HTML report as a string
        """
        # Start with header
        html_parts = [self.generate_html_header()]
        
        # Add overall summary chart
        html_parts.append('<div class="chart-container">')
        html_parts.append(self.create_overall_summary_chart(test_results))
        html_parts.append('</div>')
        
        # Add performance comparison chart
        html_parts.append('<div class="chart-container">')
        html_parts.append(self.create_performance_comparison_chart(test_results))
        html_parts.append('</div>')
        
        # Add each action section
        for action_name, test_data in test_results.items():
            html_parts.append(self.generate_action_section(action_name, test_data))
        
        # Add summary section
        html_parts.append(self.generate_summary_section(test_results))
        
        # Add footer
        html_parts.append(self.generate_footer())
        
        return ''.join(html_parts)
    
    def save_report(self, test_results: Dict, filename: str = None) -> str:
        """Save the HTML report to a file.
        
        Args:
            test_results: All test results
            filename: Optional filename (defaults to timestamped name)
            
        Returns:
            The filename where the report was saved
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vibe_test_report_{timestamp}.html"
        
        html_content = self.generate_full_report(test_results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename