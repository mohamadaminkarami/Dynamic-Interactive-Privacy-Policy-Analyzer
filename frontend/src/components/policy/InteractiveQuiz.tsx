import React, { useState, useEffect } from 'react';
import { InteractiveQuiz, QuizQuestion, QuizOption, QuizResult } from '../../types/policy';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';

interface InteractiveQuizProps {
  quiz: InteractiveQuiz;
  onComplete?: (result: QuizResult) => void;
  onClose?: () => void;
}

interface QuizState {
  currentQuestionIndex: number;
  answers: Record<string, string>;
  isComplete: boolean;
  score: number;
  showResults: boolean;
  startTime: number;
}

const InteractiveQuizComponent: React.FC<InteractiveQuizProps> = ({ quiz, onComplete, onClose }) => {
  const [state, setState] = useState<QuizState>({
    currentQuestionIndex: 0,
    answers: {},
    isComplete: false,
    score: 0,
    showResults: false,
    startTime: Date.now(),
  });

  const [swipeDirection, setSwipeDirection] = useState<'left' | 'right' | null>(null);
  const [dragOffset, setDragOffset] = useState(0);

  const currentQuestion = quiz.questions[state.currentQuestionIndex];
  const isLastQuestion = state.currentQuestionIndex === quiz.questions.length - 1;
  const isFirstQuestion = state.currentQuestionIndex === 0;

  const handleAnswerSelect = (questionId: string, answer: string) => {
    setState(prev => ({
      ...prev,
      answers: {
        ...prev.answers,
        [questionId]: answer
      }
    }));
  };

  const handleNextQuestion = () => {
    if (state.currentQuestionIndex < quiz.questions.length - 1) {
      setState(prev => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex + 1
      }));
    }
  };

  const handlePrevQuestion = () => {
    if (state.currentQuestionIndex > 0) {
      setState(prev => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex - 1
      }));
    }
  };

  const handleSwipeGesture = (info: PanInfo) => {
    const threshold = 100;
    const velocity = info.velocity.x;
    
    if (Math.abs(info.offset.x) > threshold) {
      if (info.offset.x > 0 && !isFirstQuestion) {
        // Swipe right - go to previous question
        setSwipeDirection('right');
        setTimeout(() => {
          handlePrevQuestion();
          setSwipeDirection(null);
        }, 200);
      } else if (info.offset.x < 0 && !isLastQuestion && currentQuestion && state.answers[currentQuestion.id]) {
        // Swipe left - go to next question (only if answered)
        setSwipeDirection('left');
        setTimeout(() => {
          handleNextQuestion();
          setSwipeDirection(null);
        }, 200);
      }
    }
  };

  const handleTrueFalseSwipe = (info: PanInfo) => {
    if (currentQuestion?.question_type === 'true_false') {
      const threshold = 50;
      if (Math.abs(info.offset.x) > threshold) {
        const answer = info.offset.x > 0 ? 'True' : 'False';
        handleAnswerSelect(currentQuestion.id, answer);
      }
    }
  };

  const calculateScore = () => {
    let totalScore = 0;
    let maxScore = 0;

    quiz.questions.forEach((question) => {
      maxScore += question.points;
      const userAnswer = state.answers[question.id];
      
      if (userAnswer) {
        if (question.question_type === 'fill_blank') {
          // Check if fill-in-the-blank answer is correct (case-insensitive)
          const correctAnswer = question.options[0]?.text.toLowerCase();
          const userAnswerLower = userAnswer.toLowerCase();
          if (correctAnswer && userAnswerLower === correctAnswer) {
            totalScore += question.points;
          }
        } else {
          // Check if selected option is correct
          const selectedOption = question.options.find(opt => opt.text === userAnswer);
          if (selectedOption?.is_correct) {
            totalScore += question.points;
          }
        }
      }
    });

    return { totalScore, maxScore };
  };

  const handleFinishQuiz = () => {
    const { totalScore, maxScore } = calculateScore();
    const percentage = Math.round((totalScore / maxScore) * 100);
    
    const result: QuizResult = {
      quiz_id: quiz.id,
      answers: state.answers,
      score: totalScore,
      total_points: maxScore,
      percentage: percentage,
      time_taken_seconds: Math.floor((Date.now() - state.startTime) / 1000),
      passed: percentage >= 70,
      completed_at: new Date(),
    };

    setState(prev => ({
      ...prev,
      score: totalScore,
      isComplete: true,
      showResults: true,
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
      startTime: Date.now(),
    });
  };

  if (state.showResults) {
    return (
      <QuizResults 
        quiz={quiz}
        answers={state.answers}
        score={state.score}
        onRestart={resetQuiz}
        onClose={onClose}
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

  const isCurrentQuestionAnswered = state.answers[currentQuestion.id];
  const canProceed = isCurrentQuestionAnswered && !isLastQuestion;
  const canFinish = isCurrentQuestionAnswered && isLastQuestion;

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
        <motion.div 
          className="bg-gradient-to-r from-blue-500 to-purple-600 h-2"
          initial={{ width: 0 }}
          animate={{ width: `${((state.currentQuestionIndex + 1) / quiz.questions.length) * 100}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>

      {/* Swipe Instructions */}
      <div className="px-6 py-2 bg-gray-50 border-b border-gray-200">
        <div className="flex justify-between items-center text-xs text-gray-600">
          <span>💡 Swipe left/right to navigate questions</span>
          {currentQuestion.question_type === 'true_false' && (
            <span>👆 Swipe right for True, left for False</span>
          )}
        </div>
      </div>

      {/* Question Content */}
      <div className="relative overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestion.id}
            initial={{ x: swipeDirection === 'left' ? 300 : swipeDirection === 'right' ? -300 : 0, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: swipeDirection === 'left' ? -300 : swipeDirection === 'right' ? 300 : 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="p-6"
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={0.2}
            onDragEnd={(_, info) => handleSwipeGesture(info)}
            onDrag={(_, info) => setDragOffset(info.offset.x)}
          >
            {/* Question Header */}
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

              {/* Options / Input */}
              <div className="space-y-3">
                {currentQuestion.question_type === 'fill_blank' ? (
                  // Fill-in-the-blank input
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Your answer:
                    </label>
                    <input
                      type="text"
                      value={state.answers[currentQuestion.id] || ''}
                      onChange={(e) => handleAnswerSelect(currentQuestion.id, e.target.value)}
                      placeholder="Type your answer here..."
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none transition-colors"
                    />
                  </div>
                ) : currentQuestion.question_type === 'true_false' ? (
                  // True/False with swipe gestures
                  <div>
                    <div className="text-sm text-gray-600 mb-4 text-center">
                      Select an answer or use swipe gestures
                    </div>
                    <motion.div
                      className="grid grid-cols-2 gap-4"
                      drag="x"
                      dragConstraints={{ left: 0, right: 0 }}
                      dragElastic={0.2}
                      onDragEnd={(_, info) => handleTrueFalseSwipe(info)}
                    >
                      {currentQuestion.options.map((option) => (
                        <motion.button
                          key={option.id}
                          onClick={() => handleAnswerSelect(currentQuestion.id, option.text)}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className={`relative p-4 rounded-lg border-2 transition-all ${
                            state.answers[currentQuestion.id] === option.text
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-300 hover:border-gray-400'
                          }`}
                        >
                          <div className="flex items-center justify-center">
                            <span className="text-lg font-medium">{option.text}</span>
                          </div>
                          {option.text === 'True' && (
                            <div className="absolute -top-2 -right-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                              Swipe →
                            </div>
                          )}
                          {option.text === 'False' && (
                            <div className="absolute -top-2 -left-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">
                              ← Swipe
                            </div>
                          )}
                        </motion.button>
                      ))}
                    </motion.div>
                  </div>
                ) : (
                  // Multiple choice options
                  currentQuestion.options.map((option) => (
                    <motion.button
                      key={option.id}
                      onClick={() => handleAnswerSelect(currentQuestion.id, option.text)}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                      className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                        state.answers[currentQuestion.id] === option.text
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                    >
                      <div className="flex items-center">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-current mr-3 flex items-center justify-center">
                          {state.answers[currentQuestion.id] === option.text ? '✓' : ''}
                        </span>
                        <span>{option.text}</span>
                      </div>
                    </motion.button>
                  ))
                )}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <motion.button
            onClick={handlePrevQuestion}
            disabled={isFirstQuestion}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isFirstQuestion
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            ← Previous
          </motion.button>

          <div className="flex items-center gap-2">
            {/* Answer status indicator */}
            {isCurrentQuestionAnswered && (
              <motion.span
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-green-600 text-sm font-medium"
              >
                ✓ Answered
              </motion.span>
            )}
          </div>

          <div className="flex gap-2">
            {!isLastQuestion ? (
              <motion.button
                onClick={handleNextQuestion}
                disabled={!canProceed}
                whileHover={{ scale: canProceed ? 1.05 : 1 }}
                whileTap={{ scale: canProceed ? 0.95 : 1 }}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  canProceed
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                Next →
              </motion.button>
            ) : (
              <motion.button
                onClick={handleFinishQuiz}
                disabled={!canFinish}
                whileHover={{ scale: canFinish ? 1.05 : 1 }}
                whileTap={{ scale: canFinish ? 0.95 : 1 }}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  canFinish
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                Finish Quiz
              </motion.button>
            )}
          </div>
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
  onClose?: () => void;
}

const QuizResults: React.FC<QuizResultsProps> = ({ quiz, answers, score, onRestart, onClose }) => {
  const maxScore = quiz.questions.reduce((sum, q) => sum + q.points, 0);
  const percentage = Math.round((score / maxScore) * 100);
  const passed = percentage >= 70;

  // Calculate results for each question
  const questionResults = quiz.questions.map((question) => {
    const userAnswer = answers[question.id];
    let correctAnswer: string;
    let isCorrect = false;
    let explanation = '';

    if (question.question_type === 'fill_blank') {
      correctAnswer = question.options[0]?.text || '';
      isCorrect = userAnswer?.toLowerCase() === correctAnswer.toLowerCase();
    } else {
      const correctOption = question.options.find(opt => opt.is_correct);
      correctAnswer = correctOption?.text || '';
      isCorrect = userAnswer === correctAnswer;
      explanation = correctOption?.explanation || question.correct_explanation || '';
    }

    return {
      question,
      userAnswer: userAnswer || 'No answer',
      correctAnswer,
      isCorrect,
      explanation,
      points: isCorrect ? question.points : 0
    };
  });

  const correctCount = questionResults.filter(r => r.isCorrect).length;
  const incorrectCount = questionResults.length - correctCount;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden"
    >
      {/* Header Section */}
      <div className={`p-6 ${passed ? 'bg-green-50 border-b border-green-200' : 'bg-red-50 border-b border-red-200'}`}>
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className={`text-6xl mb-4 ${passed ? 'text-green-500' : 'text-red-500'}`}
          >
            {passed ? '🎉' : '📚'}
          </motion.div>
          <h3 className={`text-2xl font-bold mb-2 ${passed ? 'text-green-800' : 'text-red-800'}`}>
            {passed ? 'Congratulations!' : 'Keep Learning!'}
          </h3>
          <p className="text-gray-600 mb-4">
            {passed 
              ? 'You have successfully completed the quiz and demonstrated good understanding of this privacy policy section.'
              : 'You might want to review the content and try again to ensure you fully understand the privacy implications.'
            }
          </p>

          {/* Score Summary */}
          <div className="grid grid-cols-4 gap-4 mb-4">
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-xl font-bold text-blue-600">{score}/{maxScore}</div>
              <div className="text-xs text-gray-600">Points</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-xl font-bold text-purple-600">{percentage}%</div>
              <div className="text-xs text-gray-600">Score</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-xl font-bold text-green-600">{correctCount}</div>
              <div className="text-xs text-gray-600">Correct</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-xl font-bold text-red-600">{incorrectCount}</div>
              <div className="text-xs text-gray-600">Incorrect</div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Results */}
      <div className="p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">📋 Question-by-Question Results</h4>
        
        <div className="space-y-4">
          {questionResults.map((result, index) => (
            <motion.div
              key={result.question.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-l-4 ${
                result.isCorrect 
                  ? 'border-l-green-500 bg-green-50' 
                  : 'border-l-red-500 bg-red-50'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={`text-2xl ${result.isCorrect ? 'text-green-500' : 'text-red-500'}`}>
                    {result.isCorrect ? '✅' : '❌'}
                  </span>
                  <span className="font-medium text-gray-900">
                    Question {index + 1} ({result.question.points} point{result.question.points !== 1 ? 's' : ''})
                  </span>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  result.question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                  result.question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {result.question.difficulty}
                </span>
              </div>
              
              <h5 className="font-medium text-gray-800 mb-3">{result.question.question_text}</h5>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">Your Answer:</div>
                  <div className={`p-2 rounded text-sm ${
                    result.isCorrect 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {result.userAnswer}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">Correct Answer:</div>
                  <div className="p-2 rounded text-sm bg-green-100 text-green-800">
                    {result.correctAnswer}
                  </div>
                </div>
              </div>

              {!result.isCorrect && result.explanation && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                  <div className="text-sm font-medium text-blue-800 mb-1">💡 Explanation:</div>
                  <div className="text-sm text-blue-700">{result.explanation}</div>
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center gap-3 mt-6 pt-6 border-t border-gray-200">
          <motion.button
            onClick={onRestart}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            🔄 Take Quiz Again
          </motion.button>
          {onClose && (
            <motion.button
              onClick={onClose}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              ✖️ Close Quiz
            </motion.button>
          )}
          <motion.button
            onClick={() => window.print()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
          >
            🖨️ Print Results
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

export default InteractiveQuizComponent; 