import React from "react";
import Button from "./Button";
import "../main.css";

class Header extends React.Component<{ page: string; setPage: (p: string) => void }> {
  render() {
    const { page, setPage } = this.props;

    return (
      <header>
        <div className="headers">
          <div className="HeaderButton">
            <Button
              text="ГЛАВНАЯ"
              onClick={() => setPage("main")}
              active={page === "main"} 
            />
          </div>

          <div className="HeaderButton1">
            <Button
              text="ВОЙТИ"
              onClick={() => setPage("form")}
              active={page === "form"}
            />
          </div>
        </div>
      </header>
    );
  }
}

export default Header;

