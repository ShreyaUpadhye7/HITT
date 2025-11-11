import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const ComparativeAnalysis = ({ patientId, currentUser }) => {
    const [comparativeData, setComparativeData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchComparativeData();
    }, [patientId]);

    const fetchComparativeData = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('userToken');
            const response = await fetch(`http://localhost:5001/api/comparative-analysis/${patientId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch comparative data');
            }

            const data = await response.json();
            setComparativeData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const generatePDFReport = async (analysisId, includeComparison = true) => {
        try {
            const token = localStorage.getItem('userToken');
            const response = await fetch('http://localhost:5001/api/generate-pdf-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    patientId,
                    analysisId,
                    includeComparison
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate PDF report');
            }

            // Create blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `handwriting-analysis-report-${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            alert('Error generating PDF: ' + err.message);
        }
    };

    if (loading) {
        return (
            <div className="comparative-analysis">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Loading comparative analysis...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="comparative-analysis">
                <div className="error-message">
                    <h3>Error Loading Data</h3>
                    <p>{error}</p>
                    <button onClick={fetchComparativeData} className="nav-button">Retry</button>
                </div>
            </div>
        );
    }

    if (!comparativeData || !comparativeData.comparison) {
        return (
            <div className="comparative-analysis">
                <div className="no-comparison">
                    <h3>Insufficient Data for Comparison</h3>
                    <p>At least 2 analysis sessions are required for comparative analysis.</p>
                    <p>Current sessions: {comparativeData?.analyses?.length || 0}</p>
                </div>
            </div>
        );
    }

    const { comparison, analyses } = comparativeData;
    const { first, latest, improvement, timeline } = comparison;

    return (
        <div className="comparative-analysis">
            <div className="comparison-header">
                <h2>Comparative Analysis Dashboard</h2>
                <div className="header-actions">
                    <button 
                        onClick={() => generatePDFReport(latest._id, true)}
                        className="nav-button pdf-button"
                    >
                        📄 Generate PDF Report
                    </button>
                    <button onClick={fetchComparativeData} className="nav-button refresh-button">
                        🔄 Refresh Data
                    </button>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="comparison-summary">
                <div className="summary-card">
                    <h3>Overall Progress</h3>
                    <div className={`progress-indicator ${improvement.overallImprovement ? 'improved' : 'stable'}`}>
                        {improvement.overallImprovement ? '✅ IMPROVED' : '📊 MONITORING'}
                    </div>
                    <p>{improvement.timeSpan} days between first and latest analysis</p>
                </div>

                <div className="summary-card">
                    <h3>Confidence Change</h3>
                    <div className={`confidence-change ${improvement.confidenceChange >= 0 ? 'positive' : 'negative'}`}>
                        {improvement.confidenceChange >= 0 ? '+' : ''}{improvement.confidenceChange.toFixed(1)}%
                    </div>
                    <p>AI prediction confidence</p>
                </div>

                <div className="summary-card">
                    <h3>Questionnaire Score</h3>
                    <div className={`score-change ${improvement.questionnaireScoreChange <= 0 ? 'positive' : 'negative'}`}>
                        {improvement.questionnaireScoreChange >= 0 ? '+' : ''}{improvement.questionnaireScoreChange.toFixed(2)}
                    </div>
                    <p>Lower scores indicate improvement</p>
                </div>

                <div className="summary-card">
                    <h3>Total Sessions</h3>
                    <div className="session-count">
                        {analyses.length}
                    </div>
                    <p>Analysis sessions completed</p>
                </div>
            </div>

            {/* Before/After Comparison */}
            <div className="before-after-section">
                <h3>Before vs After Comparison</h3>
                <div className="comparison-cards">
                    <div className="comparison-card first-analysis">
                        <h4>First Analysis</h4>
                        <div className="analysis-details">
                            <p><strong>Date:</strong> {new Date(first.date).toLocaleDateString()}</p>
                            <p><strong>Outcome:</strong> <span className={`outcome ${first.combinedOutcome.toLowerCase().replace(' ', '-')}`}>{first.combinedOutcome}</span></p>
                            <p><strong>Image Confidence:</strong> {first.imageAnalysis.confidence}%</p>
                            <p><strong>Questionnaire Score:</strong> {first.questionnaireAnalysis.score}</p>
                        </div>
                    </div>

                    <div className="comparison-arrow">
                        <div className="arrow-icon">→</div>
                        <div className="progress-text">
                            {improvement.overallImprovement ? 'IMPROVEMENT' : 'MONITORING'}
                        </div>
                    </div>

                    <div className="comparison-card latest-analysis">
                        <h4>Latest Analysis</h4>
                        <div className="analysis-details">
                            <p><strong>Date:</strong> {new Date(latest.date).toLocaleDateString()}</p>
                            <p><strong>Outcome:</strong> <span className={`outcome ${latest.combinedOutcome.toLowerCase().replace(' ', '-')}`}>{latest.combinedOutcome}</span></p>
                            <p><strong>Image Confidence:</strong> {latest.imageAnalysis.confidence}%</p>
                            <p><strong>Questionnaire Score:</strong> {latest.questionnaireAnalysis.score}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Progress Timeline Chart */}
            <div className="timeline-section">
                <h3>Progress Timeline</h3>
                <div className="chart-container">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={timeline}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                                dataKey="session" 
                                label={{ value: 'Session Number', position: 'insideBottom', offset: -10 }}
                            />
                            <YAxis />
                            <Tooltip 
                                labelFormatter={(value) => `Session ${value}`}
                                formatter={(value, name) => {
                                    if (name === 'Recovery Indicator') {
                                        return [value === 1 ? 'Recovery' : 'Relapse Risk', name];
                                    }
                                    return [value, name];
                                }}
                            />
                            <Legend />
                            <Line 
                                type="monotone" 
                                dataKey="confidence" 
                                stroke="#8884d8" 
                                name="Confidence %" 
                                strokeWidth={2}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="questionnaireScore" 
                                stroke="#82ca9d" 
                                name="Questionnaire Score" 
                                strokeWidth={2}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="isRecovery" 
                                stroke="#ff7300" 
                                name="Recovery Indicator" 
                                strokeWidth={3}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Detailed Analysis History */}
            <div className="history-section">
                <h3>Complete Analysis History</h3>
                <div className="analysis-history">
                    {analyses.map((analysis, index) => (
                        <div key={analysis._id} className="history-item">
                            <div className="history-header">
                                <h4>Session {index + 1}</h4>
                                <div className="history-actions">
                                    <span className="analysis-date">
                                        {new Date(analysis.date).toLocaleDateString()}
                                    </span>
                                    <button 
                                        onClick={() => generatePDFReport(analysis._id, false)}
                                        className="nav-button small-button"
                                    >
                                        📄 PDF
                                    </button>
                                </div>
                            </div>
                            <div className="history-details">
                                <div className="detail-item">
                                    <span className="label">Combined Outcome:</span>
                                    <span className={`value outcome ${analysis.combinedOutcome.toLowerCase().replace(' ', '-')}`}>
                                        {analysis.combinedOutcome}
                                    </span>
                                </div>
                                <div className="detail-item">
                                    <span className="label">Image Analysis:</span>
                                    <span className="value">{analysis.imageAnalysis.outcome} ({analysis.imageAnalysis.confidence}%)</span>
                                </div>
                                <div className="detail-item">
                                    <span className="label">Questionnaire:</span>
                                    <span className="value">{analysis.questionnaireAnalysis.outcome} (Score: {analysis.questionnaireAnalysis.score})</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ComparativeAnalysis;