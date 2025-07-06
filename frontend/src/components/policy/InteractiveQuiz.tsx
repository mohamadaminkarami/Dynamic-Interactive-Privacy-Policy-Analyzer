import React, { useState, useEffect } from 'react';
import { InteractiveQuiz, QuizQuestion, QuizOption, QuizResult } from '../../types/privacy';

interface InteractiveQuizProps {
  quiz: InteractiveQuiz;
  onComplete?: (result: QuizResult) => void;
}

interface QuizState {
  currentQuestionIndex: number;
  answers: Record<string, string>;
  isComplete: boolean;
  score: number;
  showResults: boolean;
  startTime: number;
}

const InteractiveQuizComponent: React.FC<InteractiveQuizProps> = ({ quiz, onComplete }) => {
  const [state, setState] = useState<QuizState>({
    currentQuestionIndex: 0,
    answers: {},
    isComplete: false,
    score: 0,
    showResults: false,
    startTime: Date.now()
  });

  const currentQuestion = quiz.questions[state.currentQuestionIndex];
  const isLastQuestion = state.currentQuestionIndex === quiz.questions.length - 1;
  const hasAnswered = state.answers[currentQuestion?.id] !== undefined;

  const handleAnswerSelect = (questionId: string, optionId: string) => {
    setState(prev => ({
      ...prev,
      answers: {
        ...prev.answers,
        [questionId]: optionId
      }
    }));
  };

  const handleNextQuestion = () => {
    if (isLastQuestion) {
      completeQuiz();
    } else {
      setState(prev => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex + 1
      }));
    }
  };

  const completeQuiz = () => {
    const endTime = Date.now();
    const timeTaken = Math.round((endTime - state.startTime) / 1000);
    
    let totalScore = 0;
    let totalPoints = 0;

    // Calculate score
    quiz.questions.forEach(question => {
      totalPoints += question.points;
      const selectedOptionId = state.answers[question.id];
      if (selectedOptionId) {
        const selectedOption = question.options.find(opt => opt.id === selectedOptionId);
        if (selectedOption?.is_correct) {
          totalScore += question.points;
        }
      }
    });

    const percentage = Math.round((totalScore / totalPoints) * 100);
    const passed = percentage >= quiz.passing_score;

    const result: QuizResult = {
      quiz_id: quiz.id,
      user_id: null,
      score: totalScore,
      total_points: totalPoints,
      percentage,
      passed,
      time_taken_seconds: timeTaken,
      answers: state.answers,
      completed_at: new Date()
    };

    setState(prev => ({
      ...prev,
      isComplete: true,
      score: totalScore,
      showResults: true
    }));

    if (onComplete) {
      onComplete(result);
    }
  };

  const resetQuiz = () => {
    setState({
      currentQuestionIndex: 0,
      answers: {},
      isComplete: false,
      score: 0,
      showResults: false,
      startTime: Date.now()
    });
  };

  if (state.showResults) {
    return (
      <QuizResults 
        quiz={quiz}
        answers={state.answers}
        score={state.score}
        onRestart={resetQuiz}
      />
    );
  }

  if (!currentQuestion) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold">Quiz Error</h3>
        <p className="text-red-600">No questions available for this quiz.</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Quiz Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
        <h3 className="text-xl font-bold">{quiz.title}</h3>
        <p className="text-blue-100 mt-2">{quiz.description}</p>
        <div className="flex justify-between items-center mt-4">
          <span className="text-sm text-blue-100">
            Question {state.currentQuestionIndex + 1} of {quiz.questions.length}
          </span>
          <span className="text-sm text-blue-100">
            ⏱️ ~{quiz.estimated_time_minutes} min
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-gray-200 h-2">
        <div 
          className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 transition-all duration-300"
          style={{ width: `${((state.currentQuestionIndex + 1) / quiz.questions.length) * 100}%` }}
        />
      </div>

      {/* Question Content */}
      <div className="p-6">
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            {currentQuestion.question_text}
          </h4>
          
          {/* Difficulty and Points */}
          <div className="flex gap-2 mb-4">
            <span className={`px-2 py-1 text-xs rounded-full ${
              currentQuestion.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
              currentQuestion.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {currentQuestion.difficulty}
            </span>
            <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
              {currentQuestion.points} point{currentQuestion.points !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Options */}
          <div className="space-y-3">
            {currentQuestion.options.map((option) => {
              const isSelected = state.answers[currentQuestion.id] === option.id;
              return (
                <button
                  key={option.id}
                  onClick={() => handleAnswerSelect(currentQuestion.id, option.id)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ${
                    isSelected 
                      ? 'border-blue-500 bg-blue-50 text-blue-900' 
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center">
                    <div className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                      isSelected 
                        ? 'border-blue-500 bg-blue-500' 
                        : 'border-gray-300'
                    }`}>
                      {isSelected && (
                        <div className="w-2 h-2 bg-white rounded-full" />
                      )}
                    </div>
                    <span className={isSelected ? 'font-medium' : ''}>{option.text}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Learning Objective */}
        {currentQuestion.learning_objective && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h5 className="font-semibold text-blue-900 mb-2">💡 Learning Objective</h5>
            <p className="text-blue-800 text-sm">{currentQuestion.learning_objective}</p>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => setState(prev => ({ ...prev, currentQuestionIndex: Math.max(0, prev.currentQuestionIndex - 1) }))}
            disabled={state.currentQuestionIndex === 0}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          
          <button
            onClick={handleNextQuestion}
            disabled={!hasAnswered}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isLastQuestion ? 'Complete Quiz' : 'Next Question →'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Quiz Results Component
interface QuizResultsProps {
  quiz: InteractiveQuiz;
  answers: Record<string, string>;
  score: number;
  onRestart: () => void;
}

const QuizResults: React.FC<QuizResultsProps> = ({ quiz, answers, score, onRestart }) => {
  const totalPoints = quiz.questions.reduce((sum, q) => sum + q.points, 0);
  const percentage = Math.round((score / totalPoints) * 100);
  const passed = percentage >= quiz.passing_score;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Results Header */}
      <div className={`p-6 ${passed ? 'bg-green-50' : 'bg-red-50'}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className={`text-xl font-bold ${passed ? 'text-green-800' : 'text-red-800'}`}>
              {passed ? '🎉 Quiz Completed!' : '📚 Keep Learning!'}
            </h3>
            <p className={`mt-2 ${passed ? 'text-green-600' : 'text-red-600'}`}>
              You scored {score} out of {totalPoints} points ({percentage}%)
            </p>
          </div>
          <div className={`text-4xl font-bold ${passed ? 'text-green-600' : 'text-red-600'}`}>
            {percentage}%
          </div>
        </div>
      </div>

      {/* Results Content */}
      <div className="p-6">
        {/* Question Review */}
        <div className="space-y-4 mb-6">
          <h4 className="font-semibold text-gray-900">Question Review</h4>
          
          {quiz.questions.map((question, index) => {
            const selectedOptionId = answers[question.id];
            const selectedOption = question.options.find(opt => opt.id === selectedOptionId);
            const correctOption = question.options.find(opt => opt.is_correct);
            const isCorrect = selectedOption?.is_correct || false;

            return (
              <div key={question.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <h5 className="font-medium text-gray-900">
                    {index + 1}. {question.question_text}
                  </h5>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    isCorrect ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {isCorrect ? '✓ Correct' : '✗ Incorrect'}
                  </span>
                </div>
                
                {selectedOption && (
                  <div className="mb-2">
                    <span className="text-sm text-gray-600">Your answer: </span>
                    <span className={isCorrect ? 'text-green-600' : 'text-red-600'}>
                      {selectedOption.text}
                    </span>
                  </div>
                )}
                
                {!isCorrect && correctOption && (
                  <div className="mb-2">
                    <span className="text-sm text-gray-600">Correct answer: </span>
                    <span className="text-green-600">{correctOption.text}</span>
                  </div>
                )}
                
                <div className="bg-gray-50 rounded p-3 text-sm text-gray-700">
                  <strong>Explanation:</strong> {question.correct_explanation}
                </div>
              </div>
            );
          })}
        </div>

        {/* Key Takeaways */}
        {quiz.key_takeaways && quiz.key_takeaways.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h5 className="font-semibold text-blue-900 mb-3">🔑 Key Takeaways</h5>
            <ul className="space-y-2">
              {quiz.key_takeaways.map((takeaway, index) => (
                <li key={index} className="text-blue-800 text-sm flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  {takeaway}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-center">
          <button
            onClick={onRestart}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Retake Quiz
          </button>
        </div>
      </div>
    </div>
  );
};

export default InteractiveQuizComponent; 