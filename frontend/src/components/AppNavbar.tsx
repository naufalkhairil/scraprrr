import React from 'react';
import { Navbar, Container, Nav, Badge } from 'react-bootstrap';
import { FaRocket, FaHome, FaList, FaInfoCircle } from 'react-icons/fa';
import { Link, useLocation } from 'react-router-dom';

export const AppNavbar: React.FC = () => {
  const location = useLocation();

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="shadow-sm">
      <Container>
        <Navbar.Brand as={Link} to="/">
          <FaRocket className="me-2" />
          Scraprrr
          <Badge bg="primary" className="ms-2">v1.0</Badge>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="navbar-nav" />
        <Navbar.Collapse id="navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/" active={location.pathname === '/'}>
              <FaHome className="me-1" />
              Home
            </Nav.Link>
            <Nav.Link as={Link} to="/jobs" active={location.pathname === '/jobs'}>
              <FaList className="me-1" />
              Jobs
            </Nav.Link>
            <Nav.Link as={Link} to="/about" active={location.pathname === '/about'}>
              <FaInfoCircle className="me-1" />
              About
            </Nav.Link>
          </Nav>
          <Nav>
            <Nav.Link href="http://localhost:8000/docs" target="_blank">
              API Docs
            </Nav.Link>
            <Nav.Link href="http://localhost:7900" target="_blank">
              VNC Viewer
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};
