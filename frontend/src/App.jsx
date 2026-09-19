import { useEffect, useState } from "react";

function App() {
    const [message, setMessage] = useState("Chargement...");

    useEffect(() => {
        fetch("http://127.0.0.1:5000/api/message")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erreur HTTP : " + response.status);
                }

                return response.json();
            })
            .then(data => {
                setMessage(data.message);
            })
            .catch(error => {
                console.error(error);
                setMessage("Erreur de connexion avec Python");
            });
    }, []);

    return (
        <div>
            <h1>React</h1>
            <p>{message}</p>
        </div>
    );
}

export default App;