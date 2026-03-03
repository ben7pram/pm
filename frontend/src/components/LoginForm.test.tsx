import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "@/components/LoginForm";

describe("LoginForm", () => {
  it("renders inputs and submits successfully", async () => {
    const onSuccess = vi.fn();
    // mock fetch to return ok
    global.fetch = vi.fn(async () => ({ ok: true })) as any;
    render(<LoginForm onSuccess={onSuccess} />);

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(global.fetch).toHaveBeenCalledWith("/api/login", expect.any(Object));
    // wait for success callback
    expect(onSuccess).toHaveBeenCalled();
  });
});
