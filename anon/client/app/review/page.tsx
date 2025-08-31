// @ts-nocheck
"use client";

import { useState } from "react";
import Navbar from "@/components/navbar/navbar";
import Footer from "@/components/footer/footer";

export default function ReviewPage() {
	const [company, setCompany] = useState("");
	const [title, setTitle] = useState("");
	const [rating, setRating] = useState(5);
	const [review, setReview] = useState("");
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [error, setError] = useState(null);

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError(null);
		setIsSubmitting(true);
		try {
			console.log("Review submitted:", { company, title, rating, review });
			window.location.href = "/";
		} catch (err) {
			setError("Something went wrong. Please try again.");
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<>
			<Navbar />
			<main className="min-h-screen w-full bg-[#121212] text-white">
				<div className="max-w-3xl mx-auto px-4 py-10">
					<header className="mb-8 text-center">
						<h1 className="text-3xl md:text-4xl font-bold">Write a review</h1>
						<p className="mt-2 text-sm text-neutral-300">
							Share your experience to help others make informed decisions.
						</p>
					</header>

					<form onSubmit={handleSubmit} className="space-y-6">
						<div>
							<label htmlFor="company" className="block text-sm font-medium mb-2">
								Company / Project
							</label>
							<input
								id="company"
								type="text"
								value={company}
								onChange={(e) => setCompany(e.target.value)}
								placeholder="e.g., Anondoor"
								className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 outline-none focus:ring-2 focus:ring-neutral-500"
								required
							/>
						</div>

						<div>
							<label htmlFor="title" className="block text-sm font-medium mb-2">
								Title
							</label>
							<input
								id="title"
								type="text"
								value={title}
								onChange={(e) => setTitle(e.target.value)}
								placeholder="Summarize your review"
								className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 outline-none focus:ring-2 focus:ring-neutral-500"
								required
							/>
						</div>

						<div>
							<label htmlFor="rating" className="block text-sm font-medium mb-2">
								Rating
							</label>
							<select
								id="rating"
								value={rating}
								onChange={(e) => setRating(Number(e.target.value))}
								className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 outline-none focus:ring-2 focus:ring-neutral-500"
							>
								{[5, 4, 3, 2, 1].map((r) => (
									<option key={r} value={r}>{`${r} Star${r > 1 ? "s" : ""}`}</option>
								))}
							</select>
						</div>

						<div>
							<label htmlFor="review" className="block text-sm font-medium mb-2">
								Your review
							</label>
							<textarea
								id="review"
								value={review}
								onChange={(e) => setReview(e.target.value)}
								placeholder="Be honest, constructive, and helpful to others."
								rows={8}
								className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 outline-none focus:ring-2 focus:ring-neutral-500 resize-y"
								required
							/>
							<p className="mt-2 text-xs text-neutral-400">Max 5000 characters.</p>
						</div>

						{error && (
							<p className="text-sm text-red-400">{error}</p>
						)}

						<div className="flex items-center gap-3">
							<button
								type="submit"
								disabled={isSubmitting}
								className="inline-flex items-center justify-center rounded-md bg-white text-black px-4 py-2 text-sm font-semibold hover:bg-neutral-200 disabled:opacity-50"
							>
								{isSubmitting ? "Submitting..." : "Submit review"}
							</button>
							<button
								type="button"
								onClick={() => (window.location.href = "/")}
								className="inline-flex items-center justify-center rounded-md border border-neutral-700 px-4 py-2 text-sm font-semibold hover:bg-neutral-900"
							>
								Cancel
							</button>
						</div>
					</form>
				</div>
			</main>
			<Footer />
		</>
	);
} 