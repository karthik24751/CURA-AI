from http.server import BaseHTTPRequestHandler
import json
import urllib.parse as urlparse
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        """Set CORS headers for all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Credentials', 'false')
        # Add headers to bypass Vercel protection
        self.send_header('X-Vercel-Cache', 'MISS')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
    
    def do_GET(self):
        try:
            path = self.path.split('?')[0]
            
            # Root endpoint
            if path == '/' or path == '' or path == '/api':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                response = {
                    "message": "Welcome to CuraLink API",
                    "version": "1.0.0", 
                    "status": "operational",
                    "timestamp": datetime.utcnow().isoformat(),
                    "cors": "enabled"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Health check
            elif path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"status": "healthy"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Notifications
            elif path == '/api/notifications/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"data": []}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Patient profile
            elif path == '/api/users/patient-profile':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "id": 1,
                    "medical_condition": "Diabetes",
                    "location": "New York",
                    "age": 30
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Trials
            elif path == '/api/trials/' or path == '/api/trials/search':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "data": [
                        {
                            "nct_id": "NCT05123456",
                            "title": "Flu Vaccine in Preventing Influenza Infection in Healthy Volunteers and in Patients Who Have Undergone Stem Cell Transplant",
                            "summary": "OBJECTIVES: • Examine the humoral and cellular immune responses to influenza immunization in patients who have undergone allogeneic stem cell transplantation. • Examine the impact of graft-vs-host disease on...",
                            "condition": "Influenza",
                            "location": "New York, NY",
                            "phase": "Phase 3",
                            "status": "Recruiting"
                        },
                        {
                            "nct_id": "NCT05234567",
                            "title": "Study to Assess the Effect of AZD9291 on the Blood Levels of Simvastatin in Patients With EGFRm+ NSCLC",
                            "summary": "This is a Phase I, open-label, 2-part study in patients with a confirmed diagnosis of epidermal growth factor receptor (EGFR) mutation positive (EGFRm+) non-small cell lung cancer (NSCLC), who have progressed following prior therapy with an...",
                            "condition": "NSCLC",
                            "location": "Boston, MA",
                            "phase": "Phase 1",
                            "status": "Active"
                        },
                        {
                            "nct_id": "NCT05345678",
                            "title": "A Study of Belantamab Mafodotin to Investigate Safety, Tolerability, Pharmacokinetics, Immunogenicity and Clinical Activity in Participants With Relapsed/Refractory Multiple Myeloma",
                            "summary": "Multiple myeloma (MM) is a neoplastic plasma cell disorder that is characterized by oncologic bone lesions, anemia, hypercalcemia and renal failure. Belantamab mafodotin was well tolerated in previous studies with at least one dose of...",
                            "condition": "Multiple Myeloma",
                            "location": "Chicago, IL",
                            "phase": "Phase 2",
                            "status": "Recruiting"
                        },
                        {
                            "nct_id": "NCT05456789",
                            "title": "Alemtuzumab and Glucocorticoids in Treating Newly Diagnosed Acute Graft-Versus-Host Disease in Patients Who Have Undergone a Donor Stem Cell Transplant",
                            "summary": "OBJECTIVES: • Determine whether the administration of low-dose alemtuzumab at the onset of acute graft-versus-host disease can accelerate withdrawal of glucocorticoids and decrease morbidity in patients who have undergone...",
                            "condition": "Graft vs Host Disease",
                            "location": "Los Angeles, CA",
                            "phase": "Phase 2",
                            "status": "Recruiting"
                        },
                        {
                            "nct_id": "NCT05567890",
                            "title": "The Psychosocial Burden of Families with Childhood Blood Cancer",
                            "summary": "Cancer is the second leading cause of death for children and leukemia are the main common pediatric cancer diagnoses in Chile. Childhood cancer is a traumatic experience and is associated with distress, pain, and other negative experiences for patients and their families...",
                            "condition": "Childhood Blood Cancer",
                            "location": "Miami, FL",
                            "phase": "Observational",
                            "status": "Recruiting"
                        },
                        {
                            "nct_id": "NCT05678901",
                            "title": "Clonal Hematopoiesis and Blood-Cancer Risk Inferred from Blood DNA Sequence",
                            "summary": "Cancer arise from mutations in DNA. Some mutations might be present years before cancers become clinically apparent...",
                            "condition": "Blood Cancer",
                            "location": "Seattle, WA",
                            "phase": "Observational",
                            "status": "Active"
                        },
                        {
                            "nct_id": "NCT05789012",
                            "title": "Diabetes Prevention Program",
                            "summary": "A comprehensive study on diabetes prevention through lifestyle interventions...",
                            "condition": "Diabetes",
                            "location": "Houston, TX",
                            "phase": "Phase 3",
                            "status": "Recruiting"
                        },
                        {
                            "nct_id": "NCT05890123",
                            "title": "Heart Disease Prevention Study",
                            "summary": "Research on cardiovascular disease prevention methods...",
                            "condition": "Heart Disease",
                            "location": "Philadelphia, PA",
                            "phase": "Phase 2",
                            "status": "Recruiting"
                        },
                        {
                            "nct_id": "NCT05901234",
                            "title": "Cancer Immunotherapy Trial",
                            "summary": "Novel immunotherapy approaches for cancer treatment...",
                            "condition": "Cancer",
                            "location": "San Francisco, CA",
                            "phase": "Phase 1",
                            "status": "Recruiting"
                        },
                        {
                            "nct_id": "NCT06012345",
                            "title": "Alzheimer's Disease Research Study",
                            "summary": "Investigating new treatments for Alzheimer's disease...",
                            "condition": "Alzheimer's Disease",
                            "location": "Atlanta, GA",
                            "phase": "Phase 2",
                            "status": "Recruiting"
                        }
                    ]
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Publications
            elif path == '/api/publications/' or path == '/api/publications/search':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "data": [
                        {
                            "id": "1",
                            "title": "Advances in Cancer Immunotherapy: A Comprehensive Review",
                            "authors": "Dr. Sarah Johnson, Dr. Michael Chen, Dr. Lisa Rodriguez",
                            "journal": "Nature Medicine",
                            "year": 2024,
                            "abstract": "Recent developments in cancer immunotherapy have shown promising results..."
                        },
                        {
                            "id": "2", 
                            "title": "Machine Learning Applications in Drug Discovery",
                            "authors": "Dr. Robert Kim, Dr. Emily Watson",
                            "journal": "Science Translational Medicine",
                            "year": 2024,
                            "abstract": "AI and machine learning are revolutionizing pharmaceutical research..."
                        },
                        {
                            "id": "3",
                            "title": "CRISPR Gene Editing in Rare Diseases",
                            "authors": "Dr. Amanda Foster, Dr. David Liu",
                            "journal": "Cell",
                            "year": 2024,
                            "abstract": "Gene editing technologies offer new hope for rare disease patients..."
                        },
                        {
                            "id": "4",
                            "title": "Personalized Medicine in Oncology",
                            "authors": "Dr. Jennifer Martinez, Dr. Thomas Anderson",
                            "journal": "The Lancet Oncology",
                            "year": 2024,
                            "abstract": "Tailoring cancer treatments to individual patient profiles..."
                        },
                        {
                            "id": "5",
                            "title": "Stem Cell Therapy for Neurological Disorders",
                            "authors": "Dr. Kevin Park, Dr. Maria Gonzalez",
                            "journal": "Nature Neuroscience",
                            "year": 2024,
                            "abstract": "Regenerative medicine approaches for brain and spinal cord injuries..."
                        },
                        {
                            "id": "6",
                            "title": "Biomarkers in Alzheimer's Disease Diagnosis",
                            "authors": "Dr. Rachel Green, Dr. James Wilson",
                            "journal": "Alzheimer's & Dementia",
                            "year": 2024,
                            "abstract": "Early detection methods for neurodegenerative diseases..."
                        },
                        {
                            "id": "7",
                            "title": "Telemedicine and Digital Health Solutions",
                            "authors": "Dr. Alex Thompson, Dr. Priya Patel",
                            "journal": "JAMA",
                            "year": 2024,
                            "abstract": "The future of healthcare delivery in the digital age..."
                        },
                        {
                            "id": "8",
                            "title": "Precision Medicine in Cardiovascular Disease",
                            "authors": "Dr. Mark Davis, Dr. Susan Lee",
                            "journal": "Circulation",
                            "year": 2024,
                            "abstract": "Genomic approaches to heart disease prevention and treatment..."
                        },
                        {
                            "id": "9",
                            "title": "Microbiome Research in Human Health",
                            "authors": "Dr. Nicole Brown, Dr. Christopher Taylor",
                            "journal": "Nature Reviews Microbiology",
                            "year": 2024,
                            "abstract": "Understanding the role of gut bacteria in disease and wellness..."
                        },
                        {
                            "id": "10",
                            "title": "Artificial Intelligence in Medical Imaging",
                            "authors": "Dr. Ryan Miller, Dr. Jessica Chang",
                            "journal": "Radiology",
                            "year": 2024,
                            "abstract": "AI-powered diagnostic imaging for improved patient outcomes..."
                        }
                    ]
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Experts
            elif path == '/api/experts/' or path == '/api/experts/search':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "data": [
                        {
                            "id": 1,
                            "full_name": "Dr. Sarah Johnson",
                            "specialty": "Oncology",
                            "institution": "Memorial Sloan Kettering Cancer Center",
                            "verified": True,
                            "bio": "Leading cancer researcher with 15+ years experience in immunotherapy",
                            "location": "New York, NY"
                        },
                        {
                            "id": 2,
                            "full_name": "Dr. Michael Chen",
                            "specialty": "Cardiology",
                            "institution": "Mayo Clinic",
                            "verified": True,
                            "bio": "Cardiovascular specialist focusing on precision medicine approaches",
                            "location": "Rochester, MN"
                        }
                    ]
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Favorites
            elif path == '/api/favorites/' or path == '/api/favorites':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"data": []}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Forums
            elif path == '/api/forums/' or path == '/api/forums':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "data": [
                        {
                            "id": 1,
                            "title": "Cancer Research Discussion",
                            "description": "Share insights and discuss latest cancer research",
                            "created_by": "Dr. Sarah Johnson",
                            "created_at": "2024-11-01T10:00:00Z",
                            "posts_count": 15
                        },
                        {
                            "id": 2,
                            "title": "Clinical Trial Updates",
                            "description": "Latest updates on ongoing clinical trials",
                            "created_by": "Dr. Michael Chen",
                            "created_at": "2024-11-02T14:30:00Z",
                            "posts_count": 8
                        }
                    ]
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Meetings
            elif path == '/api/meetings/' or path == '/api/meetings':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"data": []}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # User profile
            elif path == '/api/users/me' or path == '/api/users/profile':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "id": 1,
                    "email": "user@example.com",
                    "full_name": "Test User",
                    "role": "patient"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Researcher profile
            elif path == '/api/users/researcher-profile':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "id": 1,
                    "institution": "Research University",
                    "department": "Medical Research",
                    "research_interests": "Cancer Research, Immunotherapy"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Researchers list
            elif path == '/api/users/researchers':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "data": [
                        {
                            "id": 1,
                            "full_name": "Dr. Sarah Johnson",
                            "institution": "Memorial Sloan Kettering",
                            "department": "Oncology Research",
                            "research_interests": "Cancer Immunotherapy"
                        },
                        {
                            "id": 2,
                            "full_name": "Dr. Michael Chen", 
                            "institution": "Mayo Clinic",
                            "department": "Cardiology Research",
                            "research_interests": "Precision Medicine"
                        }
                    ]
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Favicon requests
            elif path == '/favicon.ico' or path == '/favicon.png':
                self.send_response(200)
                self.send_header('Content-type', 'image/x-icon')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                # Send empty favicon
                self.wfile.write(b'')
                return
            
            # Default 200 for all other requests
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"status": "ok", "message": "CuraLink API"}
                self.wfile.write(json.dumps(response).encode())
                return
                
        except Exception as e:
            self.send_response(200)  # Always return 200 for GET
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "ok", "message": "CuraLink API"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        try:
            path = self.path.split('?')[0]
            
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8')) if post_data else {}
            except:
                data = {}
            
            # Login
            if path == '/api/auth/login':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                email = data.get('email', 'user@example.com')
                response = {
                    "access_token": f"token-{hash(email)}",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "email": email,
                        "full_name": "Demo User",
                        "role": "patient"
                    }
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Register
            elif path == '/api/auth/register':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                email = data.get('email', 'user@example.com')
                full_name = data.get('full_name', 'Demo User')
                role = data.get('role', 'patient')
                
                response = {
                    "access_token": f"token-{hash(email)}",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "email": email,
                        "full_name": full_name,
                        "role": role
                    }
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Chat AI
            elif path == '/api/chat/ai-assistant':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                message = data.get('message', '').lower()
                
                # Smart responses based on keywords
                if 'diabetes' in message:
                    ai_response = "I can help you with diabetes information! Diabetes is a condition where blood sugar levels are too high. There are effective treatments available including lifestyle changes, medications, and insulin therapy. Would you like me to find clinical trials or specialists in your area?"
                elif 'cancer' in message:
                    ai_response = "I understand you're looking for cancer information. Cancer treatment has advanced significantly with immunotherapy, targeted therapy, and precision medicine. I can help you find relevant clinical trials, oncology specialists, and the latest research publications. What specific type of cancer are you interested in?"
                elif 'heart' in message or 'cardiac' in message:
                    ai_response = "Heart health is crucial! Cardiovascular diseases can often be prevented and treated effectively. I can help you find cardiologists, heart disease prevention programs, and clinical trials for heart conditions. Are you looking for preventive care or treatment options?"
                elif 'trial' in message or 'study' in message:
                    ai_response = "Clinical trials are a great way to access cutting-edge treatments! I can help you find trials that match your condition, location, and eligibility criteria. Clinical trials often provide access to new therapies before they're widely available. What condition are you interested in?"
                elif 'doctor' in message or 'specialist' in message:
                    ai_response = "Finding the right healthcare provider is important! I can help you locate verified specialists in various fields including oncology, cardiology, endocrinology, and more. What type of specialist are you looking for, and what's your location?"
                elif 'hello' in message or 'hi' in message:
                    ai_response = "Hello! I'm CuraAI, your healthcare research assistant. I can help you find clinical trials, medical publications, connect with specialists, and answer questions about various health conditions. How can I assist you today?"
                elif 'help' in message:
                    ai_response = "I'm here to help! I can assist you with: 🔬 Finding clinical trials, 📚 Searching medical publications, 👨‍⚕️ Connecting with specialists, 💊 Information about treatments, 🏥 Healthcare resources. What would you like to explore?"
                else:
                    ai_response = f"Thank you for your question about '{message}'. As your healthcare AI assistant, I'm here to help you navigate medical research, find clinical trials, connect with specialists, and access the latest healthcare information. Could you provide more details about what specific health topic you're interested in?"
                
                response = {
                    "response": ai_response,
                    "timestamp": datetime.utcnow().isoformat(),
                    "suggestions": [
                        "Find clinical trials",
                        "Search publications", 
                        "Connect with experts",
                        "Learn about treatments"
                    ]
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Create forum
            elif path == '/api/forums/' or path == '/api/forums':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"message": "Forum created", "id": 3}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Add to favorites
            elif path == '/api/favorites/' or path == '/api/favorites':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"message": "Added to favorites", "id": 1}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Create meeting
            elif path == '/api/meetings/' or path == '/api/meetings':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"message": "Meeting created", "id": 1}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Default POST response
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"message": "Success"}
                self.wfile.write(json.dumps(response).encode())
                return
                
        except Exception as e:
            self.send_response(200)  # Always return 200 for POST
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "ok", "message": "Request processed"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_PUT(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"message": "Updated successfully"}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(200)  # Always return 200 for PUT
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "ok", "message": "Request processed"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # BULLETPROOF OPTIONS - ALWAYS 200
        try:
            print(f"OPTIONS request for path: {self.path}")
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, HEAD')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.send_header('Access-Control-Max-Age', '86400')
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', '2')
            self.end_headers()
            self.wfile.write(b'OK')
            print("OPTIONS response sent successfully")
        except Exception as e:
            print(f"OPTIONS error: {e}")
            # Even if there's an error, send 200
            try:
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', '*')
                self.send_header('Access-Control-Allow-Headers', '*')
                self.end_headers()
            except:
                pass
