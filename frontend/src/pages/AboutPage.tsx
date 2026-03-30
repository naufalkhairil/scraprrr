import React from 'react';
import { Container, Row, Col, Card, ListGroup } from 'react-bootstrap';
import { FaInfoCircle, FaBook, FaCode, FaDocker } from 'react-icons/fa';

export const AboutPage: React.FC = () => {
  return (
    <Container className="py-4">
      <Row className="mb-4">
        <Col>
          <h1>
            <FaInfoCircle className="me-2" />
            About Scraprrr
          </h1>
          <p className="text-muted">
            A modern web scraper for Traveloka.com with real-time monitoring
          </p>
        </Col>
      </Row>

      <Row>
        <Col lg={8}>
          <Card className="mb-4 shadow-sm">
            <Card.Header>
              <FaBook className="me-2" />
              What is Scraprrr?
            </Card.Header>
            <Card.Body>
              <p>
                Scraprrr is a web scraping application that extracts flight and hotel data
                from Traveloka.com. It provides both a REST API and a web interface for
                easy access to travel data.
              </p>
              <h5>Key Features</h5>
              <ListGroup variant="flush">
                <ListGroup.Item>✓ Flight search with origin/destination airports</ListGroup.Item>
                <ListGroup.Item>✓ Hotel search by location</ListGroup.Item>
                <ListGroup.Item>✓ Real-time monitoring via Selenium Grid VNC</ListGroup.Item>
                <ListGroup.Item>✓ Async job processing with status tracking</ListGroup.Item>
                <ListGroup.Item>✓ Results export to CSV and JSON</ListGroup.Item>
                <ListGroup.Item>✓ RESTful API with interactive documentation</ListGroup.Item>
              </ListGroup>
            </Card.Body>
          </Card>

          <Card className="mb-4 shadow-sm">
            <Card.Header>
              <FaCode className="me-2" />
              Technology Stack
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <h6>Backend</h6>
                  <ul>
                    <li>Python 3.9+</li>
                    <li>FastAPI</li>
                    <li>Selenium WebDriver</li>
                    <li>Pydantic</li>
                    <li>Uvicorn</li>
                  </ul>
                </Col>
                <Col md={6}>
                  <h6>Frontend</h6>
                  <ul>
                    <li>React 18</li>
                    <li>TypeScript</li>
                    <li>React Bootstrap</li>
                    <li>React Query</li>
                    <li>Vite</li>
                  </ul>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Header>
              <FaDocker className="me-2" />
              Quick Start
            </Card.Header>
            <Card.Body>
              <h6>1. Start Selenium Grid</h6>
              <pre className="bg-light p-2 rounded small">
                docker-compose -f docker/selenium-grid/docker-compose.yml up -d
              </pre>

              <h6 className="mt-3">2. Start API Server</h6>
              <pre className="bg-light p-2 rounded small">
                scraprrr-serve
              </pre>

              <h6 className="mt-3">3. Start Frontend</h6>
              <pre className="bg-light p-2 rounded small">
                cd frontend{'\n'}npm install{'\n'}npm run dev
              </pre>

              <h6 className="mt-3">Access Points</h6>
              <ListGroup>
                <ListGroup.Item>
                  <strong>Frontend:</strong> http://localhost:3000
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>API:</strong> http://localhost:8000
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>API Docs:</strong> http://localhost:8000/docs
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>VNC:</strong> http://localhost:7900
                </ListGroup.Item>
                <ListGroup.Item>
                  <strong>Selenium:</strong> http://localhost:4444
                </ListGroup.Item>
              </ListGroup>
            </Card.Body>
          </Card>

          <Card className="shadow-sm">
            <Card.Header>
              <FaInfoCircle className="me-2" />
              Important Notes
            </Card.Header>
            <Card.Body>
              <div className="alert alert-warning small">
                <strong>⚠️ Disclaimer:</strong> This tool is for educational purposes
                only. Always comply with Traveloka.com's Terms of Service and robots.txt.
                Use responsibly and at your own risk.
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};
