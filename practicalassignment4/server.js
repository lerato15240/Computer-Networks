const http = require('http');
const fs = require('fs');
const qs = require('querystring');

let userScore = 0; // Variable to store the user's score

// Function to parse the questions file and extract questions and answers
function parseQuestionsFile(fileContent) {
    const lines = fileContent.split('\n');
    const questions = [];

    let currentQuestion = { question: '', alternatives: [], correctAnswers: [] };
    lines.forEach(line => {
        if (line.startsWith('?')) {
            if (currentQuestion.question !== '') {
                questions.push(currentQuestion);
            }
            currentQuestion = { question: line.substring(1), alternatives: [], correctAnswers: [] };
        } else if (line.startsWith('+')) {
            currentQuestion.alternatives.push(line.substring(1));
            currentQuestion.correctAnswers.push(line.substring(1));
        } else if (line.startsWith('-')) {
            currentQuestion.alternatives.push(line.substring(1));
        }
    });

    if (currentQuestion.question !== '') {
        questions.push(currentQuestion);
    }

    return questions;
}

// Function to randomly select a question
function selectRandomQuestion(questions) {
    const randomIndex = Math.floor(Math.random() * questions.length);
    return questions[randomIndex];
}

const server = http.createServer((req, res) => {
    if (req.method === 'GET') {
        fs.readFile('questions.txt', 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain' });
                res.end('Internal Server Error');
            } else {
                const questions = parseQuestionsFile(data);
                const randomQuestion = selectRandomQuestion(questions);

                res.writeHead(200, { 'Content-Type': 'text/html' });
                res.write('<html><body>');
                res.write(`<h1>${randomQuestion.question}</h1>`);
                res.write(`<p>Score: ${userScore}</p>`);
                res.write('<form method="POST" action="/">');
                randomQuestion.alternatives.forEach((alt, index) => {
                    res.write(`<input type="radio" name="answer" value="${alt}"> ${String.fromCharCode(65 + index)}. ${alt}<br>`);
                });
                res.write('<input type="hidden" name="correctAnswer" value="' + randomQuestion.correctAnswers[0] + '">');
                res.write('<input type="submit" value="Submit Answer">');
                res.write('</form>');
                res.write('</body></html>');
                res.end();
            }
        });
    } else if (req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            const formData = qs.parse(body);
            const selectedAnswer = formData.answer;
            const correctAnswer = formData.correctAnswer;

            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.write('<html><body>');
            if (selectedAnswer === correctAnswer) {
                userScore++; // Increment user's score if answer is correct
                res.write('<p>Correct! Your score is now: ' + userScore + '</p>');
            } else {
                res.write('<p>Incorrect! The correct answer is: ' + correctAnswer + '</p>');
            }
            res.write('<a href="/">Go back and answer another question</a>');
            res.write('</body></html>');
            res.end();
        });
    }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});